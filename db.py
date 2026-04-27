import pyodbc

def base_conn(db):
    drivers = [
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server",
        "ODBC Driver 13 for SQL Server"
    ]

    server = "fileprepdb"
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

            print(f"Trying {driver}...")
            conn = pyodbc.connect(conn_str)
            print(f"Connected using {driver}")
            return conn

        except Exception as e:
            print(f"{driver} failed: {e}")
            last_error = e

    raise Exception(f"No working ODBC driver found: {last_error}")


def get_csdb_connection():
    return base_conn("CSDB")


def get_taxroll_connection():
    return base_conn("CSDBTaxroll")
