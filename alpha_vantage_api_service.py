from datetime import datetime
from enum import Enum

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
        self._alpha_vantage_key = alpha_vantage_key

    def get_latest(self, symbol):
        ts = TimeSeries(key=self._alpha_vantage_key, output_format='pandas')
        data, _ = ts.get_intraday(symbol, interval='1min', outputsize='compact')
        return data_to_model(data, symbol, DataType.MINUTE)

    def get_daily(self, symbol):
        ts = TimeSeries(key=self._alpha_vantage_key, output_format='pandas')
        data, _ = ts.get_daily(symbol, outputsize='compact')
        timestamp = data.index.values
        return data_to_model(data, symbol, DataType.DAY)
