# alphabt

# Overview

Backtest the trading strategy on stocks and buy(sell) at next open price when the signal appears，the following features:

- Only for long strategy so far
- stop loss
- stop profit
- TaLib feature

# Strategy Method and Property

- close_position() : when you want to close the position
- long() : buy action
- long_position -> Boolean: in long position
- short_position -> Boolean: in short position
- empty_position -> Boolean: in empty position 

# Usage

- Strategy (Only for long direction):

    Buy :  8TEMA > 13TEMA

    Sell : 13TEMA > 8TEMA

```python
class TEMA(Strategy):
		"""
		unit can be integer or ratio, which respresent the unit of stock or 
    the ratio of equity to buy stock , respectively
		"""
    def __init__(self):
        # setting your data
        self.data = data
        # setting initial capital
        self.init_capital = 100000
        # use the TaLib feature
        self.tema_8 = self.indicator('TEMA', 8)['TEMA'].vaiues
        self.tema_13 = self.indicator('TEMA', 13)['TEMA'].values



    def signal(self, index):

        super().signal(index)
        # Only buy the stock with empty position
        if (self.tema_8[index] > self.tema_13[index]) & (self.empty_position):
            self.buy()
        # Only sell with long position
        if (self.tema_13[index] > self.tema_8[index]) & (self.long_position):
            self.close_position()

bt = Backtest(TEMA, , initial_equity=10000, commission=None)
bt.run()
log, per = bt.get_report()

# plot
Bt(TEMA).get_plot(subplot_technical_index=['MA'], overlap=['TEMA'], sub_plot_param={'MA':[20, 60]}, overlap_param=None, log=log)
```

- trading  log

![Untitled](https://user-images.githubusercontent.com/51486531/109655346-232af880-7b9e-11eb-82d1-e59bda6cbb8e.png)


- performance

![Untitled 1](https://user-images.githubusercontent.com/51486531/109655366-28884300-7b9e-11eb-8297-d384e71e5c3c.png)

- Figure

    ![newplot](https://user-images.githubusercontent.com/51486531/109655384-2d4cf700-7b9e-11eb-8f0e-6e71a47efe13.png)


