from .column import Column


class Table(object):
    def __init__(self, name: str, columns: Column or list(Column) = None, mainTable: bool = False):
        self.__name = name
        self.__columns = columns
        self.__mainTable = mainTable

        if isinstance(self.columns, Column):
            self.__columns = [columns]

    def addColumn(self, column: Column or list) -> None:
        if self.__columns:
            if isinstance(column, list):
                self.__columns.extend(column)
            elif isinstance(column, Column):
                self.__columns.append(column)
            else:
                raise Exception(f" Invalid type of column: {type(column) }. Must be a {type(Column)} or {type(list(Column))}")
        else:
            if isinstance(column, Column):
                self.__columns = [column]
            elif isinstance(column, list):
                self.__columns = column
            else:
                raise Exception(f" Invalid type of column: {type(column) }. Must be a {type(Column)} or {type(list(Column))}")

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str) -> None:
        self.__name = name

    @property
    def columns(self) -> list:
        return self.__columns

    @columns.setter
    def columns(self, columns: Column or list) -> None:
        self.__columns.append(columns)