import sys
sys.path.append('../')
import pandas as pd

from typing import List, Tuple


class DataInterface:
    def __init__(self):
        pass

    def data_reset(self, data):
        data = data.rename(columns={'Open': 'open',
                                    'High': 'high',
                                    'Low': 'low',
                                    'Adj Close': 'close',
                                    'Volume': 'volume',
                                    'ticker': 'symbol'})

        data = data[['open', 'high', 'low', 'close', 'volume', 'symbol']]
        return data


class Data(DataInterface):

    def __init__(self):
        super(Data, self).__init__()

    def get(self, symbol: List, date_range: Tuple = None):

        data_list = [pd.read_pickle(f'./stock_data/{s}.pkl') for s in symbol]
        data = pd.concat(data_list, 0)
        data = self.data_reset(data)
        if date_range is not None:
            data = data[str(date_range[0]): str(date_range[1])]
        return data


class CsvData(DataInterface):
    pass






