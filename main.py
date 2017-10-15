import argparse
import json
import logging

from stock_data_saver import StockDataSaver
from alpha_vantage_api_service import AlphaVantageApiService


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="config file path")
    parser.add_argument("-s", "--symbol", help="symbols separated by ,")
    parser.add_argument("-m", "--model", help="model, specify daily or latest")
    args = parser.parse_args()

    symbols = args.symbol.split(',')
    if len(symbols) == 0:
        logging.error("No symbols specified")
        return

    with open(args.config) as config_file:
        config = json.load(config_file)
        logging.basicConfig(filename=config['LOG_PATH'], level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(message)s', )
        logging.info("DB_PATH: %s, ALPHA_VANTAGE_KEY: %s",
                     config['DB_PATH'], config['ALPHA_VANTAGE_KEY'])
        logging.info("Symbol %s", str(symbols))

        saver = StockDataSaver(config['DB_PATH'])
        api_service = AlphaVantageApiService(config['ALPHA_VANTAGE_KEY'])

        for symbol in symbols:
            if args.model == 'latest':
                models = api_service.get_latest(symbol)
            elif args.model == 'daily':
                models = api_service.get_daily(symbol)
            else:
                logging.error("No model specified")
            logging.info("%s: %d entries added", symbol, len(models))
            if len(models) == 0:
                logging.error("No models added")
                return
            logging.info("first entry: %s", models[0])
            logging.info("last entry: %s", models[-1])
            saver.save_data(models)


if __name__ == "__main__":
    main()
