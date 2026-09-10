from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import yfinance as yf
from datetime import datetime, timedelta
import traceback

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///stock_analyzer.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# All 10 NSE stocks
STOCKS = [
    {"name": "Reliance Industries", "symbol": "RELIANCE.NS"},
    {"name": "Tata Consultancy Services", "symbol": "TCS.NS"},
    {"name": "HDFC Bank", "symbol": "HDFCBANK.NS"},
    {"name": "Infosys", "symbol": "INFY.NS"},
    {"name": "ICICI Bank", "symbol": "ICICIBANK.NS"},
    {"name": "State Bank of India", "symbol": "SBIN.NS"},
    {"name": "Larsen & Toubro", "symbol": "LT.NS"},
    {"name": "ITC Limited", "symbol": "ITC.NS"},
    {"name": "Bharat Electronics", "symbol": "BHARTIARTL.NS"},
    {"name": "Axis Bank", "symbol": "AXISBANK.NS"},
]


def fetch_stock_data(symbol):
    """Fetch yfinance data for a single symbol and return calculated growth info."""
    try:
        ticker = yf.Ticker(symbol)
        today = datetime.now()

        # Download data from start date to today
        history = ticker.history(
            start="2025-12-01",
            end=today + timedelta(days=1),
            auto_adjust=False,
        )

        if history.empty:
            return None

        history = history.dropna(subset=["Close"])
        if history.empty:
            return None

        # Convert index to naive datetime for comparison
        history_index = history.index

        # Find 31 Dec 2025 or nearest previous trading day
        start_date = date(2025, 12, 31)
        # Filter dates <= 31 Dec 2025
        mask = history_index <= datetime(2025, 12, 31, 23, 59, 59)
        previous_data = history_index[mask]

        if previous_data.empty:
            return None

        # Get the nearest previous trading day (last entry <= 31 Dec 2025)
        starting_date = previous_data[-1]
        starting_price = float(history.loc[starting_date, "Close"])

        # Latest available closing price
        latest_date = history.index[-1]
        latest_price = float(history.loc[latest_date, "Close"])

        # Percentage growth
        growth = ((latest_price - starting_price) / starting_price) * 100

        status = "Positive" if growth >= 0 else "Negative"

        # Convert datetime to date object for SQLAlchemy
        start_date_obj = starting_date.date() if hasattr(starting_date, "date") else datetime.strptime(
            str(starting_date)[:10], "%Y-%m-%d"
        ).date()
        latest_date_obj = latest_date.date() if hasattr(latest_date, "date") else datetime.strptime(
            str(latest_date)[:10], "%Y-%m-%d"
        ).date()

        return {
            "name": symbol.replace(".NS", ""),
            "symbol": symbol,
            "start_price": round(starting_price, 2),
            "current_price": round(latest_price, 2),
            "growth_pct": round(growth, 2),
            "start_date": start_date_obj,
            "latest_date": latest_date_obj,
            "status": status,
        }

    except Exception as e:
        print(f"Error fetching {symbol}: {traceback.format_exc()}")
        return None


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Refresh Data button clicked
        try:
            clear_all_stocks()
        except Exception:
            pass

        for stock in STOCKS:
            data = fetch_stock_data(stock["symbol"])
            if data:
                try:
                    update_or_create_stock(stock["symbol"], data)
                except Exception as e:
                    print(f"DB error updating {stock['symbol']}: {e}")

        stocks = get_all_stocks()
        highest = stocks[0] if stocks else None

        return jsonify(
            {
                "success": True,
                "stocks": [
                    {
                        "name": s.name,
                        "symbol": s.symbol,
                        "start_price": s.start_price,
                        "current_price": s.current_price,
                        "growth_pct": s.growth_pct,
                        "start_date": s.start_date.strftime("%d %b %Y"),
                        "latest_date": s.latest_date.strftime("%d %b %Y"),
                        "status": s.status,
                    }
                    for s in stocks
                ],
                "highest": (
                    {
                        "name": highest.name,
                        "symbol": highest.symbol,
                        "growth_pct": highest.growth_pct,
                    }
                    if highest
                    else None
                ),
                "current_date": datetime.now().strftime("%d %B %Y"),
            }
        )

    # GET request - display dashboard
    stocks = get_all_stocks()

    # If no data in DB, fetch fresh data
    if not stocks:
        for stock in STOCKS:
            data = fetch_stock_data(stock["symbol"])
            if data:
                try:
                    update_or_create_stock(stock["symbol"], data)
                except Exception as e:
                    print(f"DB error initial fetch {stock['symbol']}: {e}")

        stocks = get_all_stocks()

    highest = stocks[0] if stocks else None

    return render_template(
        "index.html",
        stocks=stocks,
        highest=highest,
        current_date=datetime.now().strftime("%d %B %Y"),
    )
if __name__ == '__main__':
    app.run(debug=True, port=5001)