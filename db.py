import pyodbc
import os

def base_conn(db):
    server = os.getenv("DB_SERVER", "fileprepdb")

    drivers = [
        "ODBC Driver 18 for SQL Server"
    ]

    last_error = None

    for driver in drivers:
        try:
            conn = pyodbc.connect(
                "DRIVER={" + driver + "};"
                f"SERVER={server};"
                f"DATABASE={db};"
                "Trusted_Connection=yes;"
                "TrustServerCertificate=yes;"
            )
            print(f"Connected using {driver}")
            return conn

        except Exception as e:
            last_error = e
            print(f"{driver} failed: {e}")

    raise Exception(f"No ODBC driver worked. Last error: {last_error}")


def get_csdb_connection():
    return base_conn("CSDB")


def get_taxroll_connection():
    return base_conn("CSDBTaxroll")
