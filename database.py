import sqlite3

from flask import current_app

from .models import StockData, db


def init_db(app):
    with app.app_context():
        db.create_all()


def get_all_stocks():
    return StockData.query.order_by(StockData.growth_pct.desc()).all()


def get_stock_by_symbol(symbol):
    return StockData.query.filter_by(symbol=symbol).first()


def update_or_create_stock(symbol, data):
    stock = StockData.query.filter_by(symbol=symbol).first()
    if stock:
        stock.start_price = data["start_price"]
        stock.start_date = data["start_date"]
        stock.current_price = data["current_price"]
        stock.growth_pct = data["growth_pct"]
        stock.latest_date = data["latest_date"]
        stock.status = data["status"]
    else:
        stock = StockData(
            symbol=symbol,
            name=data["name"],
            start_price=data["start_price"],
            start_date=data["start_date"],
            current_price=data["current_price"],
            growth_pct=data["growth_pct"],
            latest_date=data["latest_date"],
            status=data["status"],
        )
        db.session.add(stock)
    db.session.commit()
    return stock


def clear_all_stocks():
    StockData.query.delete()
    db.session.commit()