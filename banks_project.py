
# Import required libraries

from io import StringIO
from pathlib import Path
from datetime import datetime
import re
import sqlite3

import requests
from bs4 import BeautifulSoup
import pandas as pd


# ---------------- CONFIGURATION ----------------

BASE_DIR = Path(__file__).resolve().parent

url = (
    "https://web.archive.org/web/20230908091635/"
    "https://en.wikipedia.org/wiki/List_of_largest_banks"
)

csv_path = BASE_DIR / "exchange_rate.csv"
output_csv_path = BASE_DIR / "Largest_banks_data.csv"
db_path = BASE_DIR / "Banks.db"
log_path = BASE_DIR / "code_log.txt"

table_attribs = ["Name", "MC_USD_Billion"]
table_name = "Largest_banks"


# ---------------- LOGGING ----------------

def log_progress(message):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} : {message}\n")


# ---------------- CREATE EXCHANGE RATE CSV ----------------

def create_exchange_rate_csv(csv_path):

    if not csv_path.exists():

        exchange_rates = {
            "Currency": ["GBP", "EUR", "INR"],
            "Rate": [0.80, 0.93, 83.00]
        }

        df = pd.DataFrame(exchange_rates)

        df.to_csv(csv_path, index=False)

        print("exchange_rate.csv created successfully.")

    else:
        print("exchange_rate.csv already exists.")


# ---------------- EXTRACTION ----------------

def extract(url, table_attribs):

    print("\nExtracting bank information...")

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    tables = soup.find_all("table", class_="wikitable")

    print("Tables found:", len(tables))

    if not tables:
        raise ValueError("No Wikipedia tables found.")

    selected_df = None

    # Identify the market capitalization table
    for i, table in enumerate(tables):

        temp_df = pd.read_html(
            StringIO(str(table))
        )[0]

        # Flatten multi-level headers if present
        if isinstance(temp_df.columns, pd.MultiIndex):
            temp_df.columns = [
                " ".join(str(x) for x in col)
                for col in temp_df.columns
            ]

        columns = [
            str(col).lower().strip()
            for col in temp_df.columns
        ]

        print(f"Table {i} columns:", columns)

        name_col = None
        market_col = None

        for col in temp_df.columns:

            col_lower = str(col).lower()

            if (
                "bank name" in col_lower
                or col_lower == "bank"
                or col_lower == "name"
            ):
                name_col = col

            if (
                "market cap" in col_lower
                or "market capitalization" in col_lower
                or "market capitalisation" in col_lower
            ):
                market_col = col

        if name_col is not None and market_col is not None:

            selected_df = temp_df[
                [name_col, market_col]
            ].copy()

            selected_df.columns = table_attribs

            print(f"Selected table: {i}")

            break

    if selected_df is None:
        raise ValueError(
            "Market capitalization table not found. "
            "Please check the printed table columns."
        )

    df = selected_df

    # Clean bank names
    df["Name"] = (
        df["Name"]
        .astype(str)
        .str.replace(r"\[\d+\]", "", regex=True)
        .str.strip()
    )

    # Clean market capitalization values
    df["MC_USD_Billion"] = (
        df["MC_USD_Billion"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace(r"\[\d+\]", "", regex=True)
        .str.extract(r"(\d+(?:\.\d+)?)")[0]
    )

    df["MC_USD_Billion"] = pd.to_numeric(
        df["MC_USD_Billion"],
        errors="coerce"
    )

    # Remove invalid records
    df = df.dropna(
        subset=["Name", "MC_USD_Billion"]
    )

    df = df[df["Name"].str.lower() != "nan"]

    df = df.reset_index(drop=True)

    print("\nExtracted Data:")
    print(df.head())

    return df


# ---------------- TRANSFORMATION ----------------

def transform(df, csv_path):

    print("\nTransforming bank information...")

    exchange_rate = pd.read_csv(csv_path)

    exchange_rate_dict = dict(
        zip(
            exchange_rate["Currency"],
            exchange_rate["Rate"]
        )
    )

    for currency in ["GBP", "EUR", "INR"]:

        if currency not in exchange_rate_dict:
            raise ValueError(
                f"Missing exchange rate: {currency}"
            )

        df[f"MC_{currency}_Billion"] = (
            df["MC_USD_Billion"]
            * float(exchange_rate_dict[currency])
        ).round(2)

    print("\nTransformed Data:")
    print(df.head())

    return df


# ---------------- LOAD TO CSV ----------------

def load_to_csv(df, output_path):

    df.to_csv(output_path, index=False)

    print(f"\nCSV file saved: {output_path.name}")


# ---------------- LOAD TO DATABASE ----------------

def load_to_db(df, sql_connection, table_name):

    df.to_sql(
        table_name,
        sql_connection,
        if_exists="replace",
        index=False
    )

    print("\nData loaded into SQLite database.")


# ---------------- RUN SQL QUERY ----------------

def run_query(query_statement, sql_connection):

    result = pd.read_sql_query(
        query_statement,
        sql_connection
    )

    print(result.to_string(index=False))


# ---------------- MAIN EXECUTION ----------------

def main():

    log_progress(
        "Preliminaries complete. Initiating ETL process"
    )

    # Create exchange rate CSV if missing
    create_exchange_rate_csv(csv_path)

    # Extraction
    df = extract(url, table_attribs)

    log_progress(
        "Data extraction complete. Initiating Transformation"
    )

    # Transformation
    df = transform(df, csv_path)

    log_progress(
        "Data transformation complete. Initiating Loading"
    )

    # Save CSV
    load_to_csv(df, output_csv_path)

    log_progress("Data saved to CSV file")

    # SQLite database
    with sqlite3.connect(db_path) as sql_connection:

        log_progress("SQL Connection initiated")

        load_to_db(
            df,
            sql_connection,
            table_name
        )

        log_progress("Data loaded to Database")

        # Query 1
        print("\nAll Banks:")

        run_query(
            f"SELECT * FROM {table_name}",
            sql_connection
        )

        # Query 2
        print("\nTop 5 Banks by USD Market Cap:")

        run_query(
            f"""
            SELECT Name, MC_USD_Billion
            FROM {table_name}
            ORDER BY MC_USD_Billion DESC
            LIMIT 5
            """,
            sql_connection
        )

        # Query 3
        print("\nBanks with Market Cap over 300 Billion USD:")

        run_query(
            f"""
            SELECT Name
            FROM {table_name}
            WHERE MC_USD_Billion > 300
            """,
            sql_connection
        )

        log_progress("Process Complete")

    log_progress("Server Connection closed")

    print("\nETL PROCESS COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
