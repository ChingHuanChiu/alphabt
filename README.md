# alphabt

# Overview

Back test the strategy on stocks  and buy(sell) at next open when the signal appears，the following features:

- stop loss
- stop profit
- position overweight
- TaLib feature

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
        # input your data
        self.data = data
        self.init_capital = 100000
        self.tema = self.indicator('TEMA', [8, 13, 21, 34, 55])

    def signal(self, index):

        if (self.tema['8TEMA'][index] > self.tema['13TEMA'][index]) & (self.empty_position):
            self.buy()
        if (self.tema['13TEMA'][index] > self.tema['8TEMA'][index]) & (self.long_position):
            self.sell()

log, per = Bt(TEMA, commission=None).run()
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


# Future Work
- strategy simulation 
- CsvData class 

