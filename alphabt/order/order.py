from typing import Union, Optional

class Order:
    
    def __init__(self, 
                 ticker: str,
                 unit: Union[int, float],
                 action: str,
                 stop_loss_price: Optional[float] = None,
                 stop_profit_price: Optional[float] = None,
                 entry_date: Optional[str] = None,
                 exit_date: Optional[str] = None,
                 entry_price: Optional[float] = None,
                 exit_price: Optional[float] = None,
                 commission_cost: Optional[float] = None,
                 tax_cost: Optional[float] = None
                 ):
        """
        @param action: type of action which include 'long'、'short' and 'close'
        """
        
        self.ticker = ticker
        self.unit = unit
        self.action = action
        self.stop_loss_price = stop_loss_price
        self.stop_profit_price = stop_profit_price
        self.entry_date = entry_date
        self.exit_date = exit_date
        self.entry_price = entry_price
        self.exit_price = exit_price
        self.commission_cost = commission_cost
        self.tax_cost = tax_cost
        
    
    def __repr__(self):
    
        info = {'ticker': self.ticker,
                'unit': self.unit,
                'action': self.action,
                'entry_date': self.entry_date,
                'exit_data': self.exit_date,
                'entry_price': self.entry_price,
                'exit_price': self.exit_price,
                'stop_loss_price': self.stop_loss_price,
                'stop_profit_price': self.stop_profit_price,
                'commission_cost': self.commission_cost,
                'tax_cost': self.tax_cost
                }
    
        return f"""{info}""" 