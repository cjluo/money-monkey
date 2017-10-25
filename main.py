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
                prev_models = dao.load_daily_data(
                    symbol, models[-1].timestamp.date(), n + movavg - 2)
                prev_close = []
                last_close = []
                for prev_model in prev_models:
                    prev_close.append(prev_model.close)
                for model in models:
                    last_close.append(model.close)

            elif args.model == 'daily':
                models = api_service.get_daily(symbol)
                prev_models = models[-(n + movavg - 1):]
                prev_close = []
                for prev_model in prev_models[:-1]:
                    prev_close.append(prev_model.close)
                last_close = [models[-1].close]

            else:
                logging.error("No model specified")
            logging.info("%s: %d entries added", symbol, len(models))
            if len(models) == 0:
                logging.error("No models added")
                return
            logging.info("first entry: %s", models[0])
            logging.info("last entry: %s", models[-1])

            if len(prev_close) == (n + movavg - 2):
                data = data_processor.get_relative_movavg(
                    prev_close, last_close)
                result = inference.do_inference(data)

                if len(result) == 1:
                    models[-1].score = result[0]
                else:
                    for i in range(len(result)):
                        models[i].score = result[i]
            else:
                logging.error("Does not have enough history for inference")

            dao.save_data(models)


if __name__ == "__main__":
    main()
