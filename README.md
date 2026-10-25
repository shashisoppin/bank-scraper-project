# Largest Banks ETL Pipeline Using Python

## Project Overview

This project implements an ETL (Extract, Transform, Load) pipeline using Python to collect and process information about the world's largest banks based on market capitalization.

The application extracts banking data from an archived Wikipedia webpage, cleans and transforms the information using Pandas, converts market capitalization into multiple currencies, and stores the processed data in CSV and SQLite database formats.

It also executes SQL queries to retrieve useful banking information and maintains execution logs.

## Technologies Used

- Python
- Pandas
- BeautifulSoup
- Requests
- SQLite3
- SQL
- HTML Web Scraping

## ETL Workflow

**1. Extraction**

- Retrieve banking information from an archived Wikipedia webpage.
- Parse HTML using BeautifulSoup.
- Identify the relevant market capitalization table.
- Extract bank names and market capitalization values.

**2. Transformation**

- Clean extracted banking data.
- Handle missing and invalid values.
- Convert market capitalization from USD into GBP, EUR and INR.
- Round converted values to two decimal places.

**3. Loading**

- Export transformed data into a CSV file.
- Store processed records in an SQLite database.
- Execute SQL queries for data retrieval.

## Project Structure

```text
bank-scraper-project/
│
├── banks_project.py
├── exchange_rate.csv
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation and Setup

**1. Clone the repository**

```bash
git clone https://github.com/shashisoppin/bank-scraper-project.git
```

**2. Navigate to the project directory**

```bash
cd bank-scraper-project
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Run the application**

```bash
python banks_project.py
```

An internet connection is required to retrieve the archived webpage.

## Exchange Rate Configuration

The program automatically creates `exchange_rate.csv` if the file does not exist.

Example exchange rates:

| Currency | Rate |
|---|---:|
| GBP | 0.80 |
| EUR | 0.93 |
| INR | 83.00 |

These are illustrative rates and can be modified according to project requirements.

## Generated Output Files

After successful execution, the following files are generated:

| File | Description |
|---|---|
| Largest_banks_data.csv | Transformed banking information |
| Banks.db | SQLite database |
| code_log.txt | ETL execution logs |

## SQL Queries

The application performs the following SQL operations:

**Retrieve all bank records**

```sql
SELECT * FROM Largest_banks;
```

**Retrieve the top five banks by market capitalization**

```sql
SELECT Name, MC_USD_Billion
FROM Largest_banks
ORDER BY MC_USD_Billion DESC
LIMIT 5;
```

**Retrieve banks with market capitalization above 300 billion USD**

```sql
SELECT Name
FROM Largest_banks
WHERE MC_USD_Billion > 300;
```

## Key Features

- Automated web scraping
- Data cleaning and transformation
- Currency conversion
- Automatic CSV file creation
- SQLite database integration
- SQL query execution
- Timestamp-based execution logging
- Modular Python functions

## Learning Outcomes

Through this project, I gained practical experience in:

- Implementing an ETL pipeline using Python.
- Extracting structured data from HTML webpages.
- Processing datasets using Pandas.
- Performing currency conversions.
- Working with SQLite databases.
- Writing SQL queries.
- Organizing Python code into reusable functions.

## Data Source

Archived Wikipedia: List of Largest Banks

https://web.archive.org/web/20230908091635/https://en.wikipedia.org/wiki/List_of_largest_banks

## Future Improvements

- Add automated data validation.
- Implement error handling for unavailable data sources.
- Add unit testing.
- Visualize banking data using charts.

---

**Project Type:** Python ETL / Data Engineering Portfolio Project
