import pandas as pd
from sqlalchemy import create_engine
import os

DB_URL = "postgresql://postgres:kdsql@localhost:5432/olist_db"
engine = create_engine(DB_URL)

DATA_DIR = "data/"

tables = {
    "orders":    "olist_orders_dataset.csv",
    "items":     "olist_order_items_dataset.csv",
    "products":  "olist_products_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "payments":  "olist_order_payments_dataset.csv",
    "sellers":   "olist_sellers_dataset.csv",
}

for table_name, filename in tables.items():
    filepath = os.path.join(DATA_DIR, filename)
    df = pd.read_csv(filepath)
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print(f"Loaded {table_name:12s} → {len(df):,} rows ✅")

print("\nAll tables loaded successfully!")