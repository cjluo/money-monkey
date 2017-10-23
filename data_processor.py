import pandas as pd
import numpy as np


class DataProcessor:
    def __init__(self, movavg):
        self._movavg = movavg

    def get_relative_movavg(self, close):
        close_series = pd.Series(close)
        close_series = close_series.rolling(
            window=self._movavg, center=False).mean()
        close_movavg = close_series.values

        relative_close_movavg = close / close_movavg
        relative_close_movavg = relative_close_movavg[~np.isnan(
            relative_close_movavg)]
        relative_close_movavg = np.float32(relative_close_movavg)
        return relative_close_movavg
