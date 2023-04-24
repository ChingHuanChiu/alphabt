
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots


from alphabt.common import statistic, talibindicator 




def add_trace(fig, tech_df, row):
    """畫技術指標
    """
    
    for col in tech_df.columns:
        fig.add_trace(go.Scatter(x=tech_df.index, y=tech_df[col],
                                 mode='lines',
                                 name=col, line=dict(width=1)), row=row, col=1)


def _main_fig(data, fig, callback):
    fig.add_trace(go.Candlestick(x=data.index, open=data['open'], high=data['high'],
                                 low=data['low'],
                                 close=data['close'],
                                 name='K Bar'
                                 ), secondary_y=False, row=1, col=1)

    fig.add_trace(go.Scatter(x=data.index, y=data['close'],
                             mode='lines',
                             name='close'), row=1, col=1)

    fig.add_trace(go.Bar(name='volume', x=data.index, y=data['volume'], marker=dict(color=data.diag,
                                                                                    line=dict(color=data.diag,
                                                                                              width=1.0, )))
                  , secondary_y=True, row=1, col=1)

    if callback:
        for function in callback:
            fig.add_trace(go.Scatter(x=data.index, y=function(),
                                     mode='lines',
                                     name=f'{function().name}'), secondary_y=True, row=1, col=1)


def _update_layout(fig):
    fig.update_layout(
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        xaxis=dict(type='category'),
        height=800, width=1000)


def _subplot_indicator(subplot_technical_index, sub_plot_param, data, fig, row):
    if subplot_technical_index:
        for n, ind in enumerate(subplot_technical_index):
            if sub_plot_param is not None:
                try:
                    df_list = []
                    for timeperiod in sub_plot_param[ind]:
                        _df = talibindicator .indicator(data=data, name=ind, timeperiod=timeperiod)
                        _df.columns = [f"{timeperiod}{ind}"]
                        df_list.append(_df)
                    df = pd.concat(df_list, 1)
                except:
                    df = talibindicator .indicator(data=data, name=ind)

            else:
                df = talibindicator.indicator(data=data, name=ind)

            add_trace(fig, df, row=row + n)

    else:
        pass


def get_plotly(data, subplot_technical_index: list, overlap=None, sub_plot_param=None, overlap_param=None,
               log=None, callback: list = None):
    data = data.copy()
    data['diag'] = np.empty(len(data))
    data.diag[data.close > data.close.shift()] = '#f6416c'
    data.diag[data.close <= data.close.shift()] = '#7bc0a3'
    data.index = data.index.strftime("%Y/%m/%d")

    if log is not None:
        if subplot_technical_index:
            subplot_titles = ["收盤價", "累積報酬率", 'MDD(%)'] + [x for x in subplot_technical_index]
            length_subplot_technical_index = len(subplot_technical_index)
        else:
            subplot_titles = ["收盤價", "累積報酬率", 'MDD(%)']
            length_subplot_technical_index = 0
        row_heights = [450] + [300] * (2 + length_subplot_technical_index)
        specs = [[{"secondary_y": True}]] * (3 + length_subplot_technical_index)

        fig = make_subplots(rows=3 + length_subplot_technical_index, cols=1, row_heights=row_heights, shared_xaxes=True,
                            subplot_titles=subplot_titles, specs=specs)
        _update_layout(fig)
        _main_fig(data=data, fig=fig, callback=callback)
        date = pd.Index(np.where(log.KeepDay > 0, log.SellDate, log.BuyDate))

        _log = pd.DataFrame(index=data.index)
        buy = pd.Series(log['BuyPrice'].values, index=log['BuyDate']).drop_duplicates().rename('BuyPrice')
        sell = pd.Series(log['SellPrice'].values, index=log['SellDate']).drop_duplicates().rename('SellPrice')
        _log = pd.concat([buy, sell, _log], 1)
        try:
            
            index_start_year = min(log['BuyDate'][0].year, log['SellDate'][0].year)
            index_end_year = max(log['BuyDate'].iloc[-1].year, log['SellDate'].iloc[-1].year)
            index_return = statistic.index_accumulate_return(str(index_start_year), str(index_end_year), index='^GSPC')
        except Exception as e:
            # TODO: catch the e message
            index_return = [0] * len(log)


        fig.add_trace(go.Scatter(x=date, y=log['累積報酬率(%)'],
                                 mode='lines',
                                 name='累積報酬率(%)', ), row=2, col=1)
        fig.add_trace(go.Scatter(x=date,
                                 y=index_return[log['SellDate']],
                                 mode='lines',
                                 name='大盤累積報酬率(%)', ), row=2, col=1)

        fig.add_trace(go.Scatter(x=data.index, y=_log['BuyPrice'],
                                 mode='markers',
                                 name='Buydate'), row=1, col=1)

        fig.add_trace(go.Scatter(x=data.index, y=_log['SellPrice'],
                                 mode='markers',
                                 name='Selldate'), row=1, col=1)

        fig.add_trace(go.Scatter(x=date, y=log['MDD(%)'] * -1, fill='tozeroy', name='MDD'), row=3, col=1)
        _subplot_indicator(subplot_technical_index, sub_plot_param, data, fig, row=4)
    else:
        if subplot_technical_index:
            subplot_titles = ["收盤價"] + [x for x in subplot_technical_index]
            length_subplot_technical_index = len(subplot_technical_index)
        else:
            subplot_titles = ["收盤價"]
            length_subplot_technical_index = 0

        row_heights = [450] + [300] * length_subplot_technical_index
        specs = [[{"secondary_y": True}]] * (1 + length_subplot_technical_index)
        fig = make_subplots(rows=1 + length_subplot_technical_index, cols=1, row_heights=row_heights, shared_xaxes=True,
                            subplot_titles=subplot_titles, specs=specs)
        _update_layout(fig)
        _main_fig(data=data, fig=fig, callback=callback)
        _subplot_indicator(subplot_technical_index, sub_plot_param, data, fig, row=2)

    if overlap is not None:
        for ind in overlap:
            if overlap_param is not None:
                # overlappara={'MA': [5, 10, 20]}
                for timeperiod in overlap_param[ind]:
                    _df = talibindicator .indicator(data=data, name=ind, timeperiod=timeperiod)
                    _df.columns = [f"{timeperiod}{ind}"]
                    add_trace(fig, _df, row=1)
            else:

                add_trace(fig, talibindicator.indicator(data=data, name=ind), row=1)

    fig.show()

    # plotly.offline
