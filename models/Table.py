from abc import ABC
from pandas import DataFrame
from pymysql.cursors import Cursor
from sqlalchemy.engine import ResultProxy


class Table(DataFrame, ABC):
    """
    pandas.DataFrame inherited class defines a result table from db
    """

    def __init__(self, source, **kwargs):
        if isinstance(source, ResultProxy):
            kwargs.update({'data': source, 'columns': source.keys()})
        elif isinstance(source, Cursor):
            kwargs.update({'data': source.fetchall(), 'columns': [i[0] for i in source.description]})
        elif isinstance(source, (list, tuple)):
            kwargs.update({'data': source})
        elif isinstance(source, list) and isinstance(source[0], dict):
            kwargs.update({'data': [list(r.values()) for r in source], 'columns': list(source[0].keys())})
        super(Table, self).__init__(**kwargs)
