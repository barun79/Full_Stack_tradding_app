from fastapi import FastAPI, Request
import sqlite3
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from datetime import datetime
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

DB_PATH = '/Users/barunsingh/Projects/FullStack_Trading_App/app.db'

@app.get("/")
def index(request: Request):
    # Create a new connection and cursor for each request
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("SELECT id, company, symbol FROM stock order by symbol")
    stocks = cursor.fetchall()

    connection.close()  # Close connection after query

    return templates.TemplateResponse(
        "index.html", {"request": request, "stocks": stocks}
    )

@app.get("/stock/{symbol}")
def stock_detail(request: Request, symbol):
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("SELECT id, company, symbol FROM stock WHERE symbol = ?", (symbol,))
    stock = cursor.fetchone()
    if not stock:
        connection.close()
        return templates.TemplateResponse("not_found.html", {"request": request, "symbol": symbol})

    cursor.execute("SELECT * FROM stock_price WHERE stock_id = ? ORDER BY date DESC", (stock["id"],))
    stock_detail = cursor.fetchall()
    connection.close()

    formatted_stock_detail = []
    for row in stock_detail:
        dt = datetime.strptime(row['date'], "%Y-%m-%d")
        formatted_date = dt.strftime("%B %d, %Y")  # e.g., June 26, 2025

        formatted_stock_detail.append({
            'date': formatted_date,
            'open': row['open'],
            'high': row['high'],
            'low': row['low'],
            'close': row['close'],
            'adjust_close': row['adjust_close'],
            'volume': row['volume'],
        })

    # Pass JSON string of formatted_stock_detail to template
    stock_data_json = json.dumps(formatted_stock_detail)

    return templates.TemplateResponse(
        "stock_detail.html",
        {
            "request": request,
            "stock": stock,
            "stock_detail": formatted_stock_detail,
            "stock_data_json": stock_data_json
        }
    )

@app.get("/api/search")
def api_search(q: str = ""):
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    like_query = f"%{q}%"
    cursor.execute("""
        SELECT id, company, symbol 
        FROM stock 
        WHERE symbol LIKE ? OR company LIKE ?
        ORDER BY
            CASE
                WHEN symbol LIKE ? THEN 0
                ELSE 1
            END,
            symbol
        LIMIT 20
    """, (like_query, like_query, like_query))


    results = cursor.fetchall()
    connection.close()

    # Convert rows to list of dicts for JSON
    stocks_list = [dict(row) for row in results]

    return JSONResponse(stocks_list)