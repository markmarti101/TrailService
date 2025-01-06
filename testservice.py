import pyodbc

try:
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=dist-6-505.uopnet.plymouth.ac.uk;"
        "DATABASE=COMP2001_MMartirosyan;"
        "UID=MMartirosyan;"
        "PWD=FcxR807*;"
    )
    print("Connection successful!")
    conn.close()
except pyodbc.Error as e:
    print(f"Connection failed: {e}")
