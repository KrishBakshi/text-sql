import pandas as pd
import sqlite3
from config import EXCEL_PATH, DB_PATH, TABLE_NAME

def excel_to_sql():
    df = pd.read_excel(EXCEL_PATH)
    print(f"Excel Columns: {df.columns.tolist()}")

    conn = sqlite3.connect(DB_PATH)
    df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()

    print(f"✅ Converted {EXCEL_PATH} → {DB_PATH} (Table: {TABLE_NAME})")

if __name__ == "__main__":
    excel_to_sql()
