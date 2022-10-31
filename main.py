import argparse
import json
import logging

from stock_dao import StockDao
from alpha_vantage_api_service import AlphaVantageApiService
from time import sleep


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="config file path")
    parser.add_argument("-m", "--model", help="model, specify daily or latest")
    args = parser.parse_args()

    with open(args.config) as config_file:
        config = json.load(config_file)
        logging.basicConfig(
            filename=config["LOG_PATH"],
            level=logging.DEBUG,
            format="%(asctime)s %(levelname)s %(message)s",
        )
        logging.info(
            "DB_PATH: %s, ALPHA_VANTAGE_KEY: %s",
            config["DB_PATH"],
            config["ALPHA_VANTAGE_KEY"],
        )

        dao = StockDao(config["DB_PATH"])
        api_service = AlphaVantageApiService(config["ALPHA_VANTAGE_KEY"])

        symbols = config["STOCK"].split(",")
        logging.info("Symbol %s", str(symbols))

        if len(symbols) == 0:
            logging.error("No symbols specified")
            return

        need_wait = False
        # Alphavantage limits 5 APIs per minute.
        for symbol_list in list(chunks(symbols, 5)):
            if need_wait:
                # Wait for 1min for alpha vantage rate API cool down.
                sleep(60)

            need_wait = True

            for symbol in symbol_list:
                if args.model == "latest":
                    models = api_service.get_latest(symbol)
                    if models is None:
                        logging.error("Symbol %s reach API limit, sleep 1min", symbol)
                        sleep(60)
                        continue

                elif args.model == "daily":
                    models = api_service.get_daily(symbol)
                    if models is None:
                        logging.error("Symbol %s reach API limit, sleep 1min", symbol)
                        sleep(60)
                        continue

                else:
                    logging.error("No model specified")
                    return

                logging.info("%s: %d entries added", symbol, len(models))
                if len(models) == 0:
                    logging.error("No models added")
                    return
                logging.info("first entry: %s", models[0])
                logging.info("last entry: %s", models[-1])
                dao.save_data(models)

            logging.info("Processed %s" % str(symbol_list))


if __name__ == "__main__":
    main()
