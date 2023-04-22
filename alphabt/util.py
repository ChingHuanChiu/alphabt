
import pandas as pd



def reset_data(data_frame: pd.DataFrame) -> pd.DataFrame:

    data_frame['date'] = pd.to_datetime(data_frame.index)

    data_frame.columns = [c.lower() for c in data_frame.columns]


    data_frame = data_frame[['date', 'open', 'high', 'low', 'close', 'volume', 'ticker']]
    return data_frame




def print_result(sharpe, calmar) -> None:
    print('-----------------------------|')
    print('sharpe ratio', '|', sharpe, '--------|')
    print('-----------------------------|')
    print('calmar ratio', '|', calmar, '--------|')
    print('-----------------------------|')



