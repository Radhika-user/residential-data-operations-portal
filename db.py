import pyodbc
import platform

def base_conn(db):
    if platform.system() != "Windows":
        raise Exception("Windows Authentication works only on Windows machines")

    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=fileprepdb;"
        f"DATABASE={db};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

    return pyodbc.connect(conn_str)


def get_csdb_connection():
    return base_conn("CSDB")


def get_taxroll_connection():
    return base_conn("CSDBTaxroll")
