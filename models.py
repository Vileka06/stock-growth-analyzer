from datetime import date, datetime
from . import db


class StockData(db.Model):
    __tablename__ = "stock_data"

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    start_price = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    growth_pct = db.Column(db.Float, nullable=False)
    latest_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"<StockData {self.symbol}>"