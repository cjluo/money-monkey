import pandas as pd
import numpy as np


class DataProcessor:
    def __init__(self, movavg):
        self._movavg = movavg

    def get_relative_movavg(self, close, last_close):
        # close: n - 1 np array
        # last_close: m np array
        # Returns m x n np array

        m = len(last_close)

        new_close = close + [last_close[-1]]
        close_series = pd.Series(new_close)
        close_series = close_series.rolling(
            window=self._movavg, center=False).mean()
        close_movavg = close_series.values

        relative_close_movavg = new_close / close_movavg
        relative_close_movavg = relative_close_movavg[~np.isnan(
            relative_close_movavg)]
        relative_close_movavg = np.float32(relative_close_movavg)

        ratio = last_close[-1] / relative_close_movavg[-1]
        last_close /= ratio
        result = np.repeat([relative_close_movavg], m, axis=0)
        result[:, -1] = last_close

        return result
