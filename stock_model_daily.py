from sqlalchemy import Column, Integer, String, Float, Date
from base import Base


class StockModelDaily(Base):
    __tablename__ = 'stock_daily'

    symbol = Column(String(10), primary_key=True)
    timestamp = Column(Date, primary_key=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
    score = Column(Float)

    def __init__(self, symbol, timestamp, open, high, low, close, volume):
        self.symbol = symbol
        self.timestamp = timestamp
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.score = 0

    def __repr__(self):
        return "<Stock(symbol='%s', timestamp='%s', open='%s', high='%s', low='%s', close='%s', volume='%s', score='%s')>" % (
            self.symbol, self.timestamp, self.open, self.high, self.low, self.close, self.volume, self.score)
