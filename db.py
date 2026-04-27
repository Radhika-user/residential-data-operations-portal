import pyodbc
import os
import platform


def base_conn(db):
    server = os.getenv("DB_SERVER", "fileprepdb")

    # Local Windows machine
    if platform.system() == "Windows":
        drivers = [
            "ODBC Driver 18 for SQL Server",
            "ODBC Driver 17 for SQL Server",
            "ODBC Driver 13 for SQL Server"
        ]

        last_error = None

        for driver in drivers:
            try:
                conn_str = (
                    f"DRIVER={{{driver}}};"
                    f"SERVER={server};"
                    f"DATABASE={db};"
                    "Trusted_Connection=yes;"
                    "TrustServerCertificate=yes;"
                )
                return pyodbc.connect(conn_str)

            except Exception as e:
                last_error = e

        raise Exception(f"No working ODBC driver found: {last_error}")

    # Render / Linux SQL Login
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={server};"
        f"DATABASE={db};"
        f"UID={os.getenv('DB_USER')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
        "TrustServerCertificate=yes;"
    )

    return pyodbc.connect(conn_str)


def get_csdb_connection():
    return base_conn("CSDB")


def get_taxroll_connection():
    return base_conn("CSDBTaxroll")
