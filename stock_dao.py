from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from base import Base
from datetime import datetime

from stock_model_daily import StockModelDaily
from stock_model_latest import StockModelLatest


class StockDao:
    def __init__(self, db_path):
        self._engine = create_engine('sqlite:///' + db_path)
        Base.metadata.create_all(self._engine)
        self._session = sessionmaker(bind=self._engine)

    def save_data(self, models):
        session = self._session()
        for model in models:
            if not session.query(
                    model.__class__).get((model.symbol, model.timestamp)):
                session.add(model)
        session.commit()

    def load_daily_data(self, symbol, timestamp, n):
        session = self._session()
        data = session.query(StockModelDaily).filter(
            StockModelDaily.symbol == symbol).filter(
            StockModelDaily.timestamp < timestamp).order_by(
            StockModelDaily.timestamp.desc()).limit(n).all()
        return reversed(data)

    def load_latest_score_limit(self, symbol, timestamp):
        timestamp = datetime.combine(timestamp.date(), datetime.min.time())
        session = self._session()
        max = session.query(func.max(StockModelLatest.score)).filter(
            StockModelLatest.symbol == symbol).filter(
            StockModelLatest.timestamp >= timestamp).scalar()
        min = session.query(func.min(StockModelLatest.score)).filter(
            StockModelLatest.symbol == symbol).filter(
            StockModelLatest.timestamp >= timestamp).scalar()
        return min, max
