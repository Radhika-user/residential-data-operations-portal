import pyodbc


def base_conn(db):
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 13 for SQL Server}};"
        f"SERVER=fileprepdb;"
        f"DATABASE={db};"
        f"Trusted_Connection=yes;"
    )


def get_csdb_connection():
    return base_conn("CSDB")


def get_taxroll_connection():
    return base_conn("CSDBTaxroll")
