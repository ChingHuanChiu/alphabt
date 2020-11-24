from abc import ABCMeta, abstractmethod
from talib import abstract
from broker import Broker
from accessor import position_list
import pandas as pd


class Strategy(metaclass=ABCMeta):


    @abstractmethod
    def signal(self, index):
        """
        the main strategy logic
        """

    def buy(self, unit=1, limit_price=None, stop_loss=None):

        Broker(self.equity).make_order(unit=unit, limit_price=limit_price, stop_loss=stop_loss)

    def sell(self, unit=-1, limit_price=None, stop_loss=None):

        Broker(self.equity).make_order(unit=unit, limit_price=limit_price, stop_loss=stop_loss)

    def indicator(self, name, timeperiod):

        O = self.data.loc[:, 'open'].astype('float')
        H = self.data.loc[:, 'high'].astype('float')
        L = self.data.loc[:, 'low'].astype('float')
        C = self.data.loc[:, 'close'].astype('float')
        V = self.data.loc[:, 'volume'].astype('float')
        OHLCV = {'open': O, 'high': H, 'low': L, 'close': C, 'volume': V}

        ret = pd.DataFrame(index=self.data.index)
        if timeperiod is not None:
            for t in timeperiod:
                f = getattr(abstract, name)
                output_names = f.output_names
                s = f(OHLCV, timeperiod=t)
                s = pd.to_numeric(s, errors='coerce')

                if len(output_names) == 1:
                    dic = s
                    s_df = pd.DataFrame(dic, index=self.data.index,
                                        columns=['{}'.format(t) + name])  # 當output_names=1時，s為array
                else:
                    s = s.T
                    output_names_col = [f'{n}_{str(t)}' for n in output_names]
                    s_df = pd.DataFrame(s, index=self.data.index, columns=output_names_col)  # 當output_names>1時，s為list
                ret = pd.concat([ret, s_df], axis=1)
        else:
            f = getattr(abstract, name)
            output_names = f.output_names
            s = f(OHLCV)
            s = pd.to_numeric(s, errors='coerce')
            if len(output_names) == 1:
                dic = s
                s_df = pd.DataFrame(dic, index=self.data.index, columns=[name])
            else:
                s = s.T
                s_df = pd.DataFrame(s, index=self.data.index, columns=output_names)

            ret = pd.concat([ret, s_df], axis=1)
        return ret

    @property
    def position(self):
        return position_list[-1]


