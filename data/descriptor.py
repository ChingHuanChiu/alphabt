class DataSourceDescriptor:
    def __init__(self, src=None):
        self._src = src

    def __get__(self, instance, owner) -> str:
        if instance is None:
            return self
        
        return instance.__dict__[self._src]

    def __set__(self, instance, value) -> None:
        if value is None or value not in ['yfapi', 'yflocal', 'csv']:
            raise ValueError(f'data source must be one of yfapi, yflocal or csv, {value} instead')
        instance.__dict__[self._src] = value

    def __set__name(self, owner, value) -> None:
        self._src = value