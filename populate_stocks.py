import sqlite3
import alpaca_trade_api as tradeapi
from secret_key import API_KEY, SECRET_KEY
import datetime

# Set full paths if using cron
DB_PATH = '/Users/barunsingh/Projects/FullStack_Trading_App/app.db'

# Connect to the database
connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

# Connect to Alpaca
api = tradeapi.REST(API_KEY, SECRET_KEY, base_url='https://paper-api.alpaca.markets')
assets = api.list_assets()

allowed_exchanges = {"NASDAQ", "NYSE"}

# --- STEP 1: Insert or update tradable stocks ---
tradable_symbols = set()

for asset in assets:
    if asset.tradable and asset.exchange in allowed_exchanges and asset.status == "active":
        tradable_symbols.add(asset.symbol)
        cursor.execute(
            "INSERT OR IGNORE INTO stock (symbol, company) VALUES (?, ?)",
            (asset.symbol, asset.name)
        )

# --- STEP 2: Delete stocks no longer tradable ---
cursor.execute("SELECT symbol FROM stock")
db_symbols = set(row[0] for row in cursor.fetchall())

# Find expired/untradable symbols
symbols_to_delete = db_symbols - tradable_symbols

for symbol in symbols_to_delete:
    cursor.execute("DELETE FROM stock WHERE symbol = ?", (symbol,))




# --- Save changes ---
connection.commit()

# Print update message with current time
now = datetime.datetime.now()
print(f"Database updated successfully at {now.strftime('%Y-%m-%d %H:%M:%S')}")

connection.close()


