from datetime import datetime
from enum import Enum
import logging

from alpha_vantage.timeseries import TimeSeries
from stock_api_service import StockApiService
from stock_model_latest import StockModelLatest
from stock_model_daily import StockModelDaily


class DataType(Enum):
    MINUTE = 1
    DAY = 2

def data_to_model(data, symbol, type):
    timestamp = data.index.values
    open = data['1. open'].values
    high = data['2. high'].values
    low = data['3. low'].values
    close = data['4. close'].values
    volume = data['5. volume'].values
    models = []
    for i in range(len(timestamp)):
        if type == DataType.MINUTE:
            py_timestamp = datetime.strptime(timestamp[i], '%Y-%m-%d %H:%M:%S')
            model = StockModelLatest(symbol, py_timestamp, open[i], high[i], low[i], close[i], volume[i])
        else:
            py_timestamp = datetime.strptime(timestamp[i], '%Y-%m-%d').date()
            model = StockModelDaily(symbol, py_timestamp, open[i], high[i], low[i], close[i], volume[i])
        models.append(model)
    return models

class AlphaVantageApiService(StockApiService):
    def __init__(self, alpha_vantage_key):
        self._ts = TimeSeries(key=alpha_vantage_key, output_format='pandas', retries=3)

    def get_latest(self, symbol):
        try:
            data, _ = self._ts.get_intraday(symbol, interval='1min', outputsize='compact')
            return data_to_model(data, symbol, DataType.MINUTE)
        except Exception as e:
            logger = logging.getLogger()
            logger.error(str(e))
            return None

    def get_daily(self, symbol):
        try:
            data, _ = self._ts.get_daily(symbol, outputsize='compact')
            timestamp = data.index.values
            return data_to_model(data, symbol, DataType.DAY)
        except Exception as e:
            logger = logging.getLogger()
            logger.error(str(e))
            return None
