import sqlite3
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame
from secret_key import API_KEY, SECRET_KEY
from datetime import datetime

DB_PATH = '/Users/barunsingh/Projects/FullStack_Trading_App/app.db'

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

cursor.execute("SELECT id, symbol FROM stock")
stocks = cursor.fetchall()

api = tradeapi.REST(API_KEY, SECRET_KEY, base_url='https://paper-api.alpaca.markets')

start_date = "2024-01-01"
end_date = datetime.now().strftime('%Y-%m-%d')

for stock_id, symbol in stocks:
    print(f"Fetching prices for {symbol}")

    try:
        # Fetch existing dates for this stock_id in DB
        cursor.execute("SELECT date FROM stock_price WHERE stock_id = ?", (stock_id,))
        existing_dates = set(row[0] for row in cursor.fetchall())

        bars = api.get_bars(
            symbol,
            TimeFrame.Day,
            start=start_date,
            end=end_date,
            feed='iex'
        )

        new_records_count = 0
        for bar in bars:
            date_str = bar.t.strftime('%Y-%m-%d')

            # Only insert if date not already in DB for this stock
            if date_str not in existing_dates:
                cursor.execute("""
                    INSERT INTO stock_price (stock_id, date, open, high, low, close, adjust_close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    stock_id,
                    date_str,
                    bar.o,
                    bar.h,
                    bar.l,
                    bar.c,
                    bar.c,
                    bar.v
                ))
                new_records_count += 1

        connection.commit()
        print(f"✅ {new_records_count} new records inserted for {symbol}.")

    except Exception as e:
        print(f"❌ Error for {symbol}: {e}")

connection.close()
print("✅ All stock prices populated.")
