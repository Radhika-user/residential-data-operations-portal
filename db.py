import pyodbc
import os

def base_conn(db):
    server = os.getenv("DB_SERVER", "fileprepdb")

    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={server};"
        f"DATABASE={db};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
        "Connection Timeout=3000;"
    )
    return conn

def get_csdb_connection():
    return base_conn("CSDB")

def get_taxroll_connection():
    return base_conn("CSDBTaxroll")
