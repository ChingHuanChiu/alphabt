# alphabt# alphabt

Created: Feb 25, 2021 2:41 PM
Created By: 敬桓 邱
Last Edited By: 敬桓 邱
Last Edited Time: Feb 25, 2021 5:41 PM
Status: In Review 👀
Type: Project Kickoff 🚀

# Overview

Back test the strategy on stocks  and buy(sell) at next open when the signal appears，the following features:

- stop loss
- stop profit
- position overweight

# Usage

- Strategy:

    Buy :  8TEMA > 13TEMA

    Sell : 13TEMA > 8TEMA

```python
class TEMA(Strategy):
		"""
		unit can be integer or ratio, which respresent the unit of stock or 
    the ratio of equity to buy stock , respectively
		"""
    def __init__(self):
        self.data = Data().symbol_data(symbol=['AMD'])
        self.init_capital = 100000
        self.tema = self.indicator('TEMA', [8, 13, 21, 34, 55])

    def signal(self, index):

        if (self.tema['8TEMA'][index] > self.tema['13TEMA'][index]) & (self.empty_position):
            self.buy(unit=0.99)
        if (self.tema['13TEMA'][index] > self.tema['8TEMA'][index]) & (self.long_position):
            self.sell()

log, per = Bt(TEMA, commission=None).run()
# plot
Bt(TEMA).get_plot(subplot_technical_index=['MA'], overlap=['TEMA'], sub_plot_param={'MA':[20, 60]}, overlap_param=None, log=log)
```

- trading  log

![alphabt%2001b39ba63d0f4183916c93d86d578911/Untitled.png](alphabt%2001b39ba63d0f4183916c93d86d578911/Untitled.png)

- performance

![alphabt%2001b39ba63d0f4183916c93d86d578911/Untitled%201.png](alphabt%2001b39ba63d0f4183916c93d86d578911/Untitled%201.png)

- Figure

    ![alphabt%2001b39ba63d0f4183916c93d86d578911/newplot.png](alphabt%2001b39ba63d0f4183916c93d86d578911/newplot.png)

# Future Work

- portfolio function
- strategy simulation function
- Update the figure
