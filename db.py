import pyodbc
import os

def get_driver():
    drivers = pyodbc.drivers()

    # Local Windows machine preference
    if "ODBC Driver 13 for SQL Server" in drivers:
        return "ODBC Driver 13 for SQL Server"

    if "ODBC Driver 18 for SQL Server" in drivers:
        return "ODBC Driver 18 for SQL Server"

    if "ODBC Driver 17 for SQL Server" in drivers:
        return "ODBC Driver 17 for SQL Server"

    raise Exception(f"No SQL Server ODBC driver found: {drivers}")


def base_conn(db):
    server = os.getenv("DB_SERVER", "fileprepdb")
    driver = get_driver()

    conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={db};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

    return pyodbc.connect(conn_str)

def get_csdb_connection():
    return base_conn("CSDB")

def get_taxroll_connection():
    return base_conn("CSDBTaxroll")
