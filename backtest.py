import pandas as pd

from broker import *
from strategy import Strategy


class Backtest:
    def __init__(self, strategy, data):
        self.data = data
        self.data.columns = [i.lower() for i in self.data.columns]
        self.Strategy = strategy()
        self.Broker = Broker(self.Strategy.equity)

    def run(self):
        for i in range(len(self.data) - 1):
            self.Strategy.signal(i)
            self.Broker.check_order(self.data.iloc[i + 1, :], date=self.data.index[i + 1])

            self.Broker.work(self.data.iloc[i + 1, :])

        if self.Strategy.position != 0:
            self.Broker.liquidation(pos=-self.Strategy.position, price=data.open[-1])

        record = self.Broker.get_log()
        return record


if __name__ == '__main__':
    from strategy import Strategy
    data = pd.read_pickle('sp500.pkl')
    data = data[data.symbol == 'AAPL']

    class Test(Strategy):
        def __init__(self):
            self.data = data
            self.equity = 100000
            self.ma = self.indicator('MA', [5, 10])

        def signal(self, index):
            print('pos', self.position)
            print('buy', (self.ma['5MA'][index] > self.ma['10MA'][index]) & (self.position == 0))
            print('sell', (self.ma['10MA'][index] > self.ma['5MA'][index]) & (self.position > 0))
            if (self.ma['5MA'][index] > self.ma['10MA'][index]) & (self.position == 0):
                self.buy()
            if (self.ma['10MA'][index] > self.ma['5MA'][index]) & (self.position > 0):
                self.sell()

    log = Backtest(Test, data).run()



