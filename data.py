import sys
sys.path.append('../')
import pandas as pd
import os
from sqlalchemy import create_engine

class Data:

    def __init__(self):
        self.data = pd.read_pickle('price.pkl')

    def csvdata(self, filename):
        path = os.getcwd()
        path = os.path.join(path, filename + '.csv')
        df = pd.read_csv(path, encoding='cp950')
        df.index = pd.to_datetime(df['date'])
        df.index = sorted(df.index)
        return df

    def symbol_data(self, symbol:list, sd=None, ed=None):

        data = self.data
        data['date'] = data.index

        data = data.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'})
        if symbol == 'all':
            if sd and ed:
                return data[sd:ed]
            else:
                return data
        else:
            res = pd.DataFrame()

            for s in symbol:
                sub_data = data[data['symbol'] == s][sd:ed]
                res = pd.concat([res, sub_data], 0)

            if sd and ed:
                return res[sd:ed]
            else:
                return res




