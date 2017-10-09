import json
import logging

from stock_data_saver import StockDataSaver
from alpha_vantage_api_service import AlphaVantageApiService

def main():
    logging.basicConfig(level=logging.DEBUG)

    symbols = ['AAPL', 'GOOG']
    with open('config.json') as config_file:
        config = json.load(config_file)
        logging.info("DB_PATH: %s, ALPHA_VANTAGE_KEY: %s", config['DB_PATH'], config['ALPHA_VANTAGE_KEY'])

        saver = StockDataSaver(config['DB_PATH'])
        api_service = AlphaVantageApiService(config['ALPHA_VANTAGE_KEY'])

    for symbol in symbols:
        models = api_service.get_latest(symbol)
        saver.save_data(models)
        models = api_service.get_daily(symbol)
        saver.save_data(models)


if __name__ == "__main__":
    main()