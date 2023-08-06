from .table import Table
from .query import Query


class Database(object):
    def __init__(self, name: str, table: Table or list = None):
        self.__name = name
        self.__table = table

        if isinstance(self.__table, Table):
            self.__table = [table]

    def addTable(self, table: Table or list) -> None:
        if isinstance(table, Table):
            if self.__table:
                self.__table.append(table)
            else:
                self.__table = [table]

        elif isinstance(table, list):
            if self.__table:
                self.__table.extend(table)
            else:
                self.__table = table
        else:
            raise TypeError(f" table parameter must be a Table object or list of Table objects, {type(table).__name__} passed.")

    def createQuery(self):
        return Query()

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str) -> None:
        if isinstance(name, str):
            self.__name = name
        else:
            raise TypeError(f" name parameter must be a string, {type(name).__name__} passed.")

    @property
    def table(self) -> list:
        return self.__table
    
    @table.setter
    def table(self, table: Table or list) -> None:
        if isinstance(table, Table):
            self.__table = set(table)

        elif isinstance(table, list):
            self.__table = table
        else:
            raise TypeError(f" table parameter must be a Table object or list of Table objects, {type(table).__name__} passed.")