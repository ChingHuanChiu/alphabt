from sys import path
path.extend(['./', './alphabt'])
from typing import Dict, List, Tuple, Union, Optional

import pandas as pd
import numpy as np
from talib import abstract
from numba import jit

from data.data import Data




"""TODO: need to speed up the create method in TaLibIndicator class
"""
class _TaLibIndicator:
    # maybe datasource is need to be design as a description
    Data.datasource = 'yflocal'
    d = Data()
    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data
        self.f = None
        self.parameters = None
        self.output_names = None

        self._open = self.data.open if self.data is not None else self.d.get_data('open') 
        self._close = self.data.close if self.data is not None  else self.d.get_data('close')
        self._high = self.data.high if self.data is not None  else self.d.get_data('high')
        self._low = self.data.low if self.data is not None  else self.d.get_data('low')
        self._volume = self.data.volume if self.data is not None  else self.d.get_data('volume')
        self.tickers = self.data.ticker.unique() if self.data is not None  else self._close.columns


    def create(self, name:str, timeperiod:int=None, **parameters) -> Union[pd.DataFrame, Tuple[pd.DataFrame, ...], List[pd.DataFrame]]:
        self.f = getattr(abstract, name)
        self.output_names: List[str] = self.f.output_names
        self.parameters = self.f.parameters
        output_names_length: int = len(self.output_names)

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
              timeperiod: Optional[int]=None, 
              data: Optional[pd.DataFrame]=None, 
              return_info: bool=False,
              **parameters) -> Union[pd.DataFrame, dict]:

    taindicator_instance = _TaLibIndicator(data=data)
    
    res = taindicator_instance.create(name, 
                                    timeperiod=timeperiod, 
                                    **parameters)



    if return_info:
        return {'data': res, f'{name}_info': taindicator_instance.indicator_info()}
                                
    return res



