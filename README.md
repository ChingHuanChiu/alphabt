# alphabt

# Overview

Backtest the trading strategy on stocks and buy(sell) at next open price when the signal appears，the following features:

- long stock and also can short stock
- stop loss
- stop profit
- TaLib feature

# Strategy Method and Property

- close_position() : when you want to close the position
- buy() : buy action
- sell() : sell action
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
        # Only buy the stock with empty position
        if (self.tema_8[index] > self.tema_13[index]) & (self.empty_position):
            self.buy()
        # Only sell with long position
        if (self.tema_13[index] > self.tema_8[index]) & (self.long_position):
            self.close_position()

bt = Backtest(TEMA, commission=None)
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

- Strategy (both long and short direction)
```python
class CCI(Strategy):
    def __init__(self):
        # input your data
        self.data = data
        self.init_capital = 10000
        self.cci = self.indicator('CCI')

    def signal(self, index):

        if (self.cci['CCI'][index] > -100) & (self.cci['CCI'][index - 1] < -100) & (not self.long_position):
            #先將做空部位買回，再做多
            if self.short_position:
                self.close_position()
            self.buy(unit=1, stop_loss=0.1, stop_profit=0.1)
        if (self.cci['CCI'][index] < 100) & (self.cci['CCI'][index - 1] > 100) & (not self.short_position):
            # 先賣出多頭部位，再做空
            if self.long_position:
                self.close_position()
            self.sell(unit=-1)   
```

# TODO

- UnitTest
- Develope portfolio bt
