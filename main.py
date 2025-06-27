from fastapi import FastAPI, Request
import sqlite3
from fastapi.templating import Jinja2Templates

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

    cursor.execute("SELECT id, company, symbol FROM stock where symbol = ?", (symbol,))
    stock = cursor.fetchone()
    if not stock:
        connection.close()
        return templates.TemplateResponse("not_found.html", {"request": request, "symbol": symbol})

    cursor.execute("SELECT * FROM stock_price WHERE stock_id = ?", (stock["id"],))
    stock_detail = cursor.fetchall()
    connection.close()

    return templates.TemplateResponse(
        "stock_detail.html", {"request": request, "stock": stock , "stock_detail":stock_detail }
    )