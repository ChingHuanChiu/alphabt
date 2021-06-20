import sys
sys.path.append('../')
import pandas as pd

from typing import List, Tuple

STOCK_DATA = pd.read_pickle('alphabt/stock_data/price.pkl')


class DataInterface:
    def __init__(self):
        pass

    def data_reset(self, data):
        data = data[['Open', 'High', 'Low', 'Close', 'Volume', 'ticker']]

        data = data.rename(columns={'Open': 'open',
                                    'High': 'high',
                                    'Low': 'low',
                                    'Close': 'close',
                                    'Volume': 'volume',
                                    'ticker': 'symbol'})

        return data


class Data(DataInterface):

    def __init__(self):
        super(Data, self).__init__()

    def get(self, symbol: List = None, date_range: Tuple = None):
        if symbol is None:
            data = STOCK_DATA
        else:
            data = STOCK_DATA[STOCK_DATA.ticker.isin(symbol)]
        data = self.data_reset(data)
        if date_range is not None:
            data = data[str(date_range[0]): str(date_range[1])]
        return data.round(2)


class CsvData(DataInterface):
    def __init__(self):
        pass
    pass







