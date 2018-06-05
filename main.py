import argparse
import json
import logging

from stock_dao import StockDao
from alpha_vantage_api_service import AlphaVantageApiService
from inference import Inference
from data_processor import DataProcessor
from model_presenter import plot_to_file
from email_sender import EmailSender
from time import sleep


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="config file path")
    parser.add_argument("-s", "--symbol", help="symbols separated by ,")
    parser.add_argument("-m", "--model", help="model, specify daily or latest")
    parser.add_argument(
        "-n", "--n", help="data size of the ml model", default=15)
    parser.add_argument("-a", "--movavg", help="movavg size", default=30)
    parser.add_argument(
        "-t", "--threshold", help="abs value of score notification",
        default=0.4)
    parser.add_argument(
        "-i", "--incremental", help="incremental score for new notification",
        default=0.05)
    args = parser.parse_args()

    symbols = args.symbol.split(',')
    if len(symbols) == 0:
        logging.error("No symbols specified")
        return
    n = int(args.n)
    movavg = int(args.movavg)
    threshold = float(args.threshold)
    incremental = float(args.incremental)

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
        email_sender = EmailSender(config['EMAIL'])
        title = ''
        images = {}

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
                    timestamp = []
                    for i in range(len(result)):
                        models[i].score = result[i]
                        timestamp.append(models[i].timestamp)
                    # Todo check the score range for today and
                    # see if we want to send out email.
                    score_max = result.max()
                    score_min = result.min()

                    daily_score_min, daily_score_max =\
                        dao.load_latest_score_limit(symbol, timestamp[0])

                    is_new_score = (
                        daily_score_max is None) or (
                        score_max >= daily_score_max + incremental)
                    is_new_score |= (
                        daily_score_min is None) or (
                        score_min <= daily_score_min - incremental)

                    logging.info("score_max %s, score_min %s",
                                 score_max, score_min)
                    logging.info("daily_score_max %s, daily_score_min %s",
                                 daily_score_max, daily_score_min)

                    meet_threshold = (score_max >= threshold)
                    meet_threshold |= (score_min <= -threshold)

                    if is_new_score and meet_threshold:
                        plot_file = plot_to_file(
                            symbol, timestamp, last_close, result)
                        logging.info(
                            "%s save prediction to %s", symbol, plot_file)
                        title += "%s:%0.2f, " % (symbol, result[-1])
                        images[symbol] = plot_file
            else:
                logging.error("Does not have enough history for inference")

            dao.save_data(models)
            # Sleep 2s to meet API querying limit.
            sleep(2)

        if images:
            email_sender.send_email(title, images)


if __name__ == "__main__":
    main()
