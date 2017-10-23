import argparse
import json
import logging

from stock_dao import StockDao
from alpha_vantage_api_service import AlphaVantageApiService
from inference import Inference
from data_processor import DataProcessor


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="config file path")
    parser.add_argument("-s", "--symbol", help="symbols separated by ,")
    parser.add_argument("-m", "--model", help="model, specify daily or latest")
    parser.add_argument("-n", "--n", help="data size of the ml model")
    parser.add_argument("-a", "--movavg", help="movavg size")
    args = parser.parse_args()

    symbols = args.symbol.split(',')
    if len(symbols) == 0:
        logging.error("No symbols specified")
        return
    n = int(args.n)
    movavg = int(args.movavg)

    with open(args.config) as config_file:
        config = json.load(config_file)
        logging.basicConfig(filename=config['LOG_PATH'], level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(message)s', )
        logging.info("DB_PATH: %s, ALPHA_VANTAGE_KEY: %s",
                     config['DB_PATH'], config['ALPHA_VANTAGE_KEY'])
        logging.info("Symbol %s", str(symbols))

        dao = StockDao(config['DB_PATH'])
        api_service = AlphaVantageApiService(config['ALPHA_VANTAGE_KEY'])
        inference = Inference(config['HOST'], config['WORK_DIR'])
        data_processor = DataProcessor(movavg)

        for symbol in symbols:
            if args.model == 'latest':
                models = api_service.get_latest(symbol)
                # Reversed order
                prev_models = dao.load_data(
                    symbol, models[-1].timestamp.date(), n + movavg - 2)
                close = []
                for prev_model in prev_models:
                    close.append(prev_model.close)
                close.append(models[-1].close)

            elif args.model == 'daily':
                models = api_service.get_daily(symbol)
                prev_models = models[-(n + movavg - 1):]
                close = []
                for prev_model in prev_models:
                    close.append(prev_model.close)

            else:
                logging.error("No model specified")
            logging.info("%s: %d entries added", symbol, len(models))
            if len(models) == 0:
                logging.error("No models added")
                return
            logging.info("first entry: %s", models[0])
            logging.info("last entry: %s", models[-1])

            data = data_processor.get_relative_movavg(close)
            result = inference.do_inference(data)

            dao.save_data(models)


if __name__ == "__main__":
    main()
