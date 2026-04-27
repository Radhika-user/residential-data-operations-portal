import os
import platform
import pyodbc
import pymssql


def base_conn(db):
    server = os.getenv("DB_SERVER", "fileprepdb")

    # LOCAL WINDOWS
    if platform.system() == "Windows":
        drivers = [
            "ODBC Driver 18 for SQL Server",
            "ODBC Driver 17 for SQL Server",
            "ODBC Driver 13 for SQL Server"
        ]

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
            except:
                continue

    # RENDER / LINUX
    return pymssql.connect(
        server=server,
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=db
    )


def get_csdb_connection():
    return base_conn("CSDB")


def get_taxroll_connection():
    return base_conn("CSDBTaxroll")
