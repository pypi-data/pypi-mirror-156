from .dtypes import DType


class Column(object):
    def __init__(self, name: str, dtype: type):
        self.__name = name
        self.__dtype = DType.getTypeOf(dtype)

    @property
    def name(self) -> str:
        return self.__name
    
    @name.setter
    def name(self, name: str) -> None:
        if not isinstance(name, str):
            raise Exception(f" Tipo do nome invalido, passe uma string")

        self.__name = name

    @property
    def dtype(self) -> str:
        return self.__dtype

    @dtype.setter
    def dtype(self, dtype: type) -> None:
        self.__dtype = DType.getTypeOf(dtype)