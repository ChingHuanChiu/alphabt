from sys import path
path.extend(['./', './alphabt'])
from typing import Dict, List, Tuple, Union

import pandas as pd
import numpy as np
from talib import abstract
from numba import jit

from data.data import Data



"""TODO: need to speed up the create method in TaLibIndicator class
"""
class TaLibIndicator:

    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data
        self.f = None
        self.parameters = None
        self.output_names = None
        self._open = None
        self._close = None
        self._high = None
        self._low = None
        self._volume = None
        self.tickers = None
        
        if self.data is not None:
            
            self._open: pd.Series = self.data.open
            self._close: pd.Series =self.data.close
            self._high: pd.Series = self.data.high
            self._low: pd.Series = self.data.low
            self._volume: pd.Series = self.data.volume
            self.tickers: np.array  = self.data.ticker.unique()



    def create(self, name:str, timeperiod:int=None, **parameters) -> Union[pd.DataFrame, Tuple[pd.DataFrame, ...], List[pd.DataFrame]]:
        # _dict = dict()
        self.f = getattr(abstract, name)
        self.output_names: List[str] = self.f.output_names
        self.parameters = self.f.parameters
        output_names_length: int = len(self.output_names)


        # TODO: cost tom much time , need to be corrected,  https://github.com/polakowo/vectorbt/issues/45
        _dict = {t: self.f(self._makeOHLCV(t=t), timeperiod=timeperiod, **parameters) for t in self.tickers}


        if output_names_length == 1:
            res =  pd.DataFrame(_dict, index=self._close.index)
            if self.data is not None:
                res.columns = [name]

            return res

        else:
            record_dict = dict() 
            for i in range(output_names_length):
                record_dict[i] = {t: _dict[t][i] for t in _dict.keys()}
            if self.data is not None:
                res_df = [pd.DataFrame(record_dict[i], index=self._close.index) for i in range(output_names_length)]
                res_df = pd.concat(res_df, 1)
                res_df.columns = [self.output_names]
                return res_df
            
            else:
                return tuple(pd.DataFrame(record_dict[i], index=self._close.index) for i in range(output_names_length))



    def _makeOHLCV(self, t: str = None) -> Dict[str, Union[pd.Series, pd.DataFrame]]:

        if self.data is not None:
            return {
                    'open': self._open,
                    'high': self._high,
                    'low': self._low,
                    'close':self._close,
                    'volume':self._volume
                            }
        else:
            return {
                'open': self._open[t].values,
                'high': self._high[t].values,
                'low': self._low[t].values,
                'close':self._close[t].values,
                'volume':self._volume[t].values
                        }


    @staticmethod
    def indicator_info(name):
        f = getattr(abstract, name)
        return {'output_names': f.output_names,
                'parameters': f.parameters
                            } 




def indicator(name: str, 
              timeperiod: int=None, 
              data: pd.DataFrame=None, 
              return_info: bool=False,
              **parameters) -> Union[pd.DataFrame, Tuple[pd.DataFrame, ...]]:

    taindicator_instance = TaLibIndicator(data=data)


    if data is None:
        Data.datasource = 'yflocal'
        data = Data()

        for attr in ['open', 'close', 'high', 'low', 'volume']:
            setattr(taindicator_instance, f'_{attr}', data.get_data(attr))
        setattr(taindicator_instance, 'tickers', data.get_data('close').columns)

    
    res = taindicator_instance.create(name, 
                                    timeperiod=timeperiod, 
                                    **parameters)



    if return_info:
        return {'data': res, f'{name}_info': taindicator_instance.indicator_info()}
                                
    return res



