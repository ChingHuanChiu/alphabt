from typing import Union, Optional

from abc import ABCMeta, abstractmethod


from alphabt.position.manager import PositionManager
from alphabt.equity.manager import EquityManager
from alphabt.broker.broker import Broker
from alphabt.common.talibindicator import indicator

class Strategy(metaclass=ABCMeta):


    def __init__(self) -> None:
        self.data = None
        self.init_capital = None

        self.ticker = None
        self.next_date_price = None
        self.next_date = None


    @abstractmethod
    def signal(self, index: int) -> None:
        """the main strategy logic
           NOTICE: need to super().signal() first when overide this method
           # TODO: find the way to chechk if the signal method useing 'close' method and 'super().signal'
        """
        # trading at next day (index+1) if signal appear
        self.ticker = self.data["ticker"][index+1]
        self.next_date_price = self.data["open"][index+1]
        self.next_date = self.data["date"][index+1]


    def long(self, 
             unit: Union[int, float] = None, 
             stop_loss: Optional[float] = None, 
             stop_profit: Optional[float] = None) -> None:
        
        if unit is None:
            unit = 1
        
        if self.short_position:
            # 做多平倉
            self.close(False)

        Broker.make_order(unit=unit, 
                          stop_loss=stop_loss, 
                          stop_profit=stop_profit,
                          action='long',
                          ticker=self.ticker,
                          trading_price = self.next_date_price,
                          trading_date=self.next_date
                          )


    def short(self, 
              unit: Union[int, float] = None, 
              stop_loss: Optional[float] = None, 
              stop_profit: Optional[float] = None) -> None:
        
        if unit is None:
            unit =  -1

        if self.long_position:
            # 做空平倉
            self.close(False)

        Broker.make_order(unit=unit, 
                          stop_loss=stop_loss, 
                          stop_profit=stop_profit,
                          action='short',
                          ticker=self.ticker,
                          trading_price = self.next_date_price,
                          trading_date=self.next_date,
                          )


    def close(self, send_to_queue_when_overweight: bool = True) -> None:
        """close the position 
        """
        if self.empty_position:
            return None
        
        Broker.make_order(unit=-1*PositionManager.status(), 
                          action='close',
                          ticker=self.ticker,
                          stop_loss=None, 
                          stop_profit=None,
                          trading_price = self.next_date_price,
                          trading_date=self.next_date,
                          send_to_queue_when_overweight=send_to_queue_when_overweight
                          )
   

    def indicator(self, name, timeperiod=None, return_info: bool=False, **parameters):

        return indicator(data=self.data, 
                         name=name,
                         timeperiod=timeperiod,
                         return_info=return_info,
                         **parameters
        )

            
    @property
    def position(self) -> int:
        return PositionManager.status()


    @property
    def empty_position(self) -> bool:
        return PositionManager.status() == 0


    @property
    def long_position(self) -> bool:
        return PositionManager.status() > 0


    @property
    def short_position(self) -> bool:
        return PositionManager.status() < 0

    @property
    def equity(self) -> float:

        return EquityManager.equity

    

