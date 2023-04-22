from typing import Optional, Tuple

class EquityManager:

    _equity_queue = []
    _equity = None

    def __init__(self, 
                 initial_equity: Optional[float],
                 commission: Optional[float],
                 tax: Optional[float]) -> None:
        
        if initial_equity is not None:
            self.equity = initial_equity

        self.commission = 0.0 if commission is None else commission
        self.tax = 0.0 if tax is None else tax


    @property
    def equity(self) -> float:

        return self._equity
    

    @equity.setter
    def equity(self, value: float):

        self.__class__._equity = value
        

    def add_to_queue(self) -> None:

        self.__class__._equity_queue.append(self.equity)


    def deal_with_cost_from_order(self,
                                  order, 
                                  trading_turnover_value: float) -> None:

        if order.action == 'close':
            tax_cost = trading_turnover_value * self.tax

        else:
            tax_cost = 0

        commission_cost = trading_turnover_value * self.commission

        setattr(order, 'commission_cost', commission_cost)
        setattr(order, 'tax_cost', tax_cost)

        

