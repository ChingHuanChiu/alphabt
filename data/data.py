
from typing import Dict

from data.handler import YFDataFromAPI, CsvData, Handler, DataFromLocal
from data.descriptor import DataSourceDescriptor

class _SourceField:

    field: Dict[str, Handler] = {'yfapi': YFDataFromAPI, 'csv': CsvData, 'yflocal': DataFromLocal}

class DataSource:
    source = DataSourceDescriptor()

class Data:
    datasource = None

    def __new__(cls, **kwargs):
        data_source = DataSource()
        data_source.source = cls.datasource 
        # if data_source.src  is None or data_source.src  not in ['yfapi', 'yflocal', 'csv']:
        #     raise ValueError(f'data source must be one of yfapi, yflocal or csv')
        self = _SourceField.field[data_source.source ](**kwargs)
        return self


        










