

class EquityManager:

    _equity_queue = None

    def __init__(self, initial_equity: float) -> None:
        
        self.equity = initial_equity

    @property
    def equity(self) -> float:

        return self._equity
    

    @equity.setter
    def equity(self, value: float):

        self.__class__._equity = value

