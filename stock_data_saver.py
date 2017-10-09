from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class StockDataSaver:
    def __init__(self, db_path):
        self._engine = create_engine('sqlite:///' + db_path)
        Base.metadata.create_all(self._engine)
        self._session = sessionmaker(bind=self._engine)

    def save_data(self, models):
        session = self._session()
        for model in models:
            if not session.query(model.__class__).get((model.symbol, model.timestamp)):
                session.add(model)
        session.commit()
