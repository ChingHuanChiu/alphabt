# alphabt

# Overview

Backtest the stock with long strategy or short strategy，the following features:

- long strategy or short strategy so far
- stop loss
- stop profit
- TaLib feature

# Strategy Method and Property

- close() : when you want to close the position
- long() : long action
- short(): short action
- long_position -> Boolean: in long position
- short_position -> Boolean: in short position
- empty_position -> Boolean: in empty position 

# Usage

- Strategy (long direction):

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
        # use the TaLib feature
        self.tema_8 = self.indicator('TEMA', 8)['TEMA'].vaiues
        self.tema_13 = self.indicator('TEMA', 13)['TEMA'].values


    def signal(self, index):

        super().signal(index)
        # Only buy the stock with empty position
        if (self.tema_8[index] > self.tema_13[index]) & (self.empty_position):
            self.long()
        # Only sell with long position
        if (self.tema_13[index] > self.tema_8[index]) & (self.long_position):
            self.close()

bt = Backtest(TEMA, , initial_equity=10000, commission=None)
bt.run()
log, per = bt.get_report()

# plot
Bt(TEMA).get_plot(subplot_technical_index=['MA'], overlap=['TEMA'], sub_plot_param={'MA':[20, 60]}, overlap_param=None, log=log)
```

- trading report

![My Images](./images/trading_report.png)


- performance

![My Images](./images/yearly_report.png)

- Figure

![newplot](./images/fig.png)

# TODO

1. Add feature that accept long action and short action within a single strategy
   i.e. the situation like the in_position_queue : [buy, close, sell] must be solved
2. Unit Test 