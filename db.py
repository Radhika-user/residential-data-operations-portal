import pyodbc

def base_conn(db):
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=fileprepdb;"
        f"DATABASE={db};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
        "Connection Timeout=30;"
    )

    print("Connecting with:", conn_str)

    return pyodbc.connect(conn_str)


def get_csdb_connection():
    return base_conn("CSDB")


def get_taxroll_connection():
    return base_conn("CSDBTaxroll")
