from typing import Union, Tuple
from functools import lru_cache


import yahoo_fin.stock_info as si
import pandas as pd



class Handler:

    def get_data(self):
        pass
    
  

class YFDataFromAPI(Handler):
    def __init__(self) -> None:
        super().__init__()

    def get_data(self, ticker: str, startdate, enddate, interval='1d') -> pd.DataFrame:
        data = si.get_data(ticker, startdate, enddate, interval=interval)
        return data
    


class CsvData(Handler):
    def __init__(self, **kwargs) -> None:
        super().__init__()

        self.filepath = kwargs['file_path']

    def get_data(self) -> pd.DataFrame:

        return pd.read_csv(self.filepath)



class DataFromLocal(Handler):
    def __init__(self) -> None:
        super().__init__()

        
    @lru_cache(maxsize=None)
    def get_data(self, field: str = None) -> pd.DataFrame:
        if field is None or field not in ['close', 'open', 'high', 'low', 'volume', 'adjclose']:
            raise ValueError('field must be one of [close, open, high, low, volume, adjclose]')
        return pd.read_pickle(f'alphabt/data/storage/{field}.pkl')
