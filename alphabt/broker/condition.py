

class ICondition:

    def match(self) -> bool:
        pass


class StopLossCondition(ICondition):

    @staticmethod
    def match(trigger_price: float, 
              current_price: float,
              direction: str
              ) -> bool:
        
        """the current price is set to 'close' price
        TODO: confirm that using close price as current price is an
              appropriate choice
        
        """
        if trigger_price is None:
            return False

        if direction == 'long':
            return current_price <= trigger_price
        elif direction == 'short':
            return  current_price >= trigger_price
        else:
            return None
        

class StopProfitCondition(ICondition):

    @staticmethod
    def match(trigger_price: float, 
              current_price: float,
              direction: str
             ) -> bool:
        
        """the current price is set to 'close' price
        TODO: confirm that using close price as current price is an 
              appropriate choice
        
        """
        if trigger_price is None:
            return False

        if direction == 'long':
            return current_price >= trigger_price
        elif direction == 'short':
            return  current_price <= trigger_price
        else:
            return None