from sys import path
path.extend(['./', './alpha'])

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import mpl_finance as mpf
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import  plotly
import statistic
import pandas as pd
from plotly.subplots import make_subplots

from bt import Backtest


def get_plot(df, report_df):

    fig = plt.figure(figsize=(20, 20))

    ax = fig.add_subplot(4, 1, 1)
    ax1 = fig.add_subplot(4, 1, 2)
    ax2 = fig.add_subplot(4, 1, 3)
    ax3 = fig.add_subplot(4, 1, 4)

    ax.plot(df['close'])
    ax.set_title('signal', loc='center')

    # df = df.resample('D').ffill()
    # df.to_csv('datata.csv')

    # self.df['signal'].plot(ax=ax, secondary_y=True, alpha=0.5, legend=True)
    for i in range(len(df)):
        if df['position'][i] == 1:
            ax.axvspan(
                mdates.datestr2num(df.index[i].strftime('%Y-%m-%d')) - 0.5,
                mdates.datestr2num(df.index[i].strftime('%Y-%m-%d')) + 0.5,
                facecolor='red', edgecolor='none', alpha=0.5
            )
        else:
            ax.axvspan(
                mdates.datestr2num(df.index[i].strftime('%Y-%m-%d')) - 0.5,
                mdates.datestr2num(df.index[i].strftime('%Y-%m-%d')) + 0.5,
                facecolor='green', edgecolor='none', alpha=0.5
            )

    ax1.set_title('Net Return', loc='center')

    ax1.fill_between(np.array(report_df['SellDay']), report_df['報酬率(%)'], 0, where=report_df['報酬率(%)'] >= 0,
                     facecolor='red', interpolate=True,
                     alpha=0.7)
    ax1.fill_between(np.array(report_df['SellDay']), report_df['報酬率(%)'], 0, where=report_df['報酬率(%)'] <= 0,
                     facecolor='green', interpolate=True,
                     alpha=0.7)

    report_df['累積報酬率(%)'].plot(ax=ax2)
    ax2.set_title('cum_return(%)')

    (report_df['MDD(%)'] * -1).plot(ax=ax3, kind='area')
    ax3.title.set_text('MDD(%)')
    fig.tight_layout()


def add_trace(fig, tech_df, row):
    '''
    畫技術指標
    '''
    for col in tech_df.columns:
        fig.add_trace(go.Scatter(x=tech_df.index, y=tech_df[col],
                                 mode='lines',
                                 name=col, line=dict(width=1)), row=row, col=1)


def get_plotly(data, subplot_technical_index: list, overlap=None, sub_plot_param=None, overlap_param=None, log=None):
    data['diag'] = np.empty(len(data))
    data.diag[data.close > data.close.shift()] = '#f6416c'
    data.diag[data.close <= data.close.shift()] = '#7bc0a3'
    row_heights = [450] + [300] * (2 + len(subplot_technical_index))
    specs = [[{"secondary_y": True}]] * (3 + len(subplot_technical_index))
    if subplot_technical_index:
        subplot_titles = ["收盤價", "累積報酬率", 'MDD'] + [x for x in subplot_technical_index]
    else:
        subplot_titles = ["收盤價", "累積報酬率", 'MDD']

    fig = make_subplots(rows=3 + len(subplot_technical_index), cols=1, row_heights=row_heights,shared_xaxes=True,
                        subplot_titles=subplot_titles, specs=specs)
    fig.update_layout(
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        xaxis=dict(type='category'),
        height=1200, width=1200)

    fig.add_trace(go.Candlestick(x=data.index, open=data['open'], high=data['high'],
                                 low=data['low'],
                                 close=data['close']
                                 ), secondary_y=False, row=1, col=1)

    fig.add_trace(go.Scatter(x=data.index, y=data.close,
                             mode='lines',
                             name='close'), row=1, col=1)
    fig.add_trace(go.Bar(name='volume', x=data.index, y=data.volume, marker=dict(color=data.diag,  # 设置条形图的颜色
                                                                                 line=dict(color=data.diag,width=1.0,))),
                                                                                  secondary_y=True, row=1, col=1)
    if log is not None:
        date = pd.to_datetime(np.where(log.KeepDay > 0, log.SellDay, log.BuyDay))
        empty_series = pd.Series(index=data.index)
        buy = pd.Series(log['BuyPrice'].values, index=log['BuyDay']).drop_duplicates().rename('BuyPrice')
        sell = pd.Series(log['SellPrice'].values, index=log['SellDay']).drop_duplicates().rename('SellPrice')
        _log = pd.concat([buy, sell, empty_series], 1)


        index_return = statistic.index_cummulate_return(str(log['BuyDay'][0].year), str(log['BuyDay'].iloc[-1].year), index='^GSPC')
        fig.add_trace(go.Scatter(x=date, y=log['累積報酬率(%)'],
                                 mode='lines',
                                 name='累積報酬率(%)', ), row=2, col=1)
        fig.add_trace(go.Scatter(x=date,
                                 y=index_return[log['SellDay']],
                                 mode='lines',
                                 name='大盤累積報酬率(%)', ), row=2, col=1)

        fig.add_trace(go.Scatter(x=_log.index, y=_log['BuyPrice'],
                                 mode='markers',
                                 name='Buydate'), row=1, col=1)

        fig.add_trace(go.Scatter(x=_log.index, y=_log['SellPrice'],
                                 mode='markers',
                                 name='Selldate'), row=1, col=1)

        fig.add_trace(go.Scatter(x=date, y=log['MDD(%)'] * -1, fill='tozeroy', name='MDD'), row=3, col=1)

    if overlap is not None:
        for ind in overlap:
            if overlap_param is not None:
                # overlappara={'MA': [5, 10, 20]}
                add_trace(fig, Backtest.indicator(data, ind, overlap_param[ind]), row=1)
            else:

                add_trace(fig, Backtest.indicator(data, ind), row=1)

    for n, ind in enumerate(subplot_technical_index):
        if sub_plot_param is not None:
            try:
                df = Backtest.indicator(data, ind, sub_plot_param[ind])
            except:
                df = Backtest.indicator(data, ind)

        else:
            df = Backtest.indicator(data, ind)

        add_trace(fig, df, row=4 + n)

    fig.show()
    plotly.offline

#
# class stock_analysis:
#     def __init__(self, data, st, ed):
#         self.data = data[st:ed]
#         self.data.columns = map(lambda x: x.lower(), self.data.columns)
#         self.data.index = self.data.index.format(formatter=lambda x: x.strftime('%Y-%m-%d'))
#
#     def plot(self, subplot: list, overlap=None, subpara=None, overlappara=None):
#         subplot_num = len(subplot) + 2
#         plt.figure(facecolor='gray', figsize=(20, 20))
#         ax = plt.subplot(subplot_num, 1, 1)
#
#         mpf.candlestick2_ochl(ax, self.data['open'], self.data['close'], self.data['high'], self.data['low'],
#                               width=0.6, colorup='r', colordown='g', alpha=0.75)
#
#         self.data['low'].rolling(20).min().shift(1).plot()
#         self.data['high'].rolling(20).max().shift(1).plot()
#         if overlap is not None:
#             for t in overlap:
#
#                 if overlappara is not None:
#
#                     df = Backtest.indicator(self.data, t, overlappara[t])
#
#
#                 else:
#                     df = Backtest.indicator(self.data, t)
#
#                 plt.xticks(rotation=90, size=8)
#                 ax = ax.twinx()
#                 ax.plot(df)
#
#                 # ax.set_title('{}'.format(t))
#                 ax.legend(df, loc='best')
#             # ax.set_xticklabels(self.data.index[::10], rotation=90)
#
#         ax2 = plt.subplot(subplot_num, 1, 2)
#         mpf.volume_overlay(ax2, self.data['open'], self.data['close'], self.data['volume'], colorup='r', colordown='g',
#                            width=0.5, alpha=0.8)
#
#         for n, o in enumerate(subplot):
#             if subpara is not None:
#
#                 try:
#                     # df = self._indicator(o, subpara[o])
#                     df = Backtest(self.data).indicator(o, subpara[o])
#                 except:
#                     df = Backtest(self.data).indicator(o)
#
#             else:
#                 df = Backtest(self.data).indicator(o)
#             plt.subplot(subplot_num, 1, n+3) #subplot begin from 1
#             plt.plot(df)
#             # plt.title('{}'.format(o))
#             plt.legend(df, loc='best')
#             # plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.4, hspace=0.3)
#             plt.grid(True)
#             plt.xticks([])
#
#         plt.tight_layout()
