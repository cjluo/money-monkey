from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from stock_model_daily import StockModelDaily

Base = declarative_base()


class StockDao:
    def __init__(self, db_path):
        self._engine = create_engine('sqlite:///' + db_path)
        Base.metadata.create_all(self._engine)
        self._session = sessionmaker(bind=self._engine)

    def save_data(self, models):
        session = self._session()
        for model in models:
            if not session.query(model.__class__).get(
                    (model.symbol, model.timestamp)):
                session.add(model)
        session.commit()

    def load_data(self, symbol, timestamp, n):
        session = self._session()
        data = session.query(StockModelDaily).filter(
            StockModelDaily.symbol == symbol).filter(
            StockModelDaily.timestamp < timestamp).order_by(
            StockModelDaily.timestamp.desc()).limit(n).all()
        return reversed(data)
