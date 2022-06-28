
from typing import Dict

from data.handler import YFDataFromAPI, CsvData, Handler, DataFromLocal


class _SourceField:

    field: Dict[str, Handler] = {'yfapi': YFDataFromAPI, 'csv': CsvData, 'yflocal': DataFromLocal}



class Data:
    
    _datasource = None

    def __new__(cls, **kwargs):
        if cls.datasource is None:
            raise ValueError('You must set the data source first')
        else:
            if cls.datasource not in _SourceField.field:
                raise ValueError(f'datasource must be one of {_SourceField.field.keys()}')
            else:
                self = _SourceField.field[cls.datasource](**kwargs)
        return self

    def __init__(self, **kwargs) -> None:

        ...



    @property
    @classmethod
    def datasource(cls):
        return cls._datasource


    @datasource.setter
    @classmethod
    def datasource(cls, source: str = 'yfapi'):
        """ 
            @param source str: setting the data source, default is from yahoo api 
        
        """
        cls._datasource = source









