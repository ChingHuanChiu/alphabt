
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

    def mysql(self, symbol=None, table='twe_stock', startdate=None, enddate=None):
        engine = create_engine('mysql+pymysql://root:XXXXXXXXXXX@localhost:3306/StockData')
        conn = engine.connect()
        if symbol is not None:
            try:
                if isinstance(symbol, tuple):
                    # symbol = tuple(symbol)
                    Q1 = 'select * FROM {} WHERE symbol in {} ORDER BY date ASC '.format(table, symbol)
                    df = pd.read_sql(Q1, conn)
                    df.index = pd.to_datetime(df['date'])
                    df.columns = map(lambda x: x.lower(), df.columns)
                    df.open = df.open.astype('float')
                    df.high = df.high.astype('float')
                    df.low = df.low.astype('float')
                    df.close = df.close.astype('float')
                    df.volume = df.volume.astype('float')
                    return df.drop_duplicates('date')
                else:
                    Q1 = 'select * FROM {} WHERE symbol = {} ORDER BY date ASC'.format(table, symbol)
                    df = pd.read_sql(Q1, conn)
                    df.index = pd.to_datetime(df['date'])
                    df.columns = map(lambda x: x.lower(), df.columns)
                    df.open = df.open.astype('float')
                    df.high = df.high.astype('float')
                    df.low = df.low.astype('float')
                    df.close = df.close.astype('float')
                    df.volume = df.volume.astype('float')

                    return df.drop_duplicates('date')
                    print('symbol most be tuple')
            except:
                raise TypeError('must be tuple')

        elif (startdate is not None) and (enddate is not None) and (symbol is None):
            Q1 = 'select * FROM {} WHERE  date BETWEEN {} AND {}'.format(table, startdate, enddate)
            df = pd.read_sql(Q1, conn)
            df.index = pd.to_datetime(df['date'])
            df.columns = map(lambda x: x.lower(), df.columns)
            df.open = df.open.astype('float')
            df.high = df.high.astype('float')
            df.low = df.low.astype('float')
            df.close = df.close.astype('float')
            df.volume = df.volume.astype('float')
            return df.drop_duplicates('date')
        else:
            Q1 = 'select * FROM {} ORDER BY date ASC'.format(table)
            df = pd.read_sql(Q1, conn)
            df.index = pd.to_datetime(df['date'])
            df.columns = map(lambda x: x.lower(), df.columns)
            df.open = df.open.astype('float')
            df.high = df.high.astype('float')
            df.low = df.low.astype('float')
            df.close = df.close.astype('float')
            df.volume = df.volume.astype('float')

            return df.drop_duplicates('date')

    def symbol_data(self, symbol, sd=None, ed=None):

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




