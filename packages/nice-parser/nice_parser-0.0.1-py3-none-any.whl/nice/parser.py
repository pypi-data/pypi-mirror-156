from .column import Column
from .table import Table
from .database import Database
from json import load


class MappingJson(object):
    def __init__(self, sampleFile: str, databaseName: str, tableName: str):
        self.__sampleFile = sampleFile
        self.__databaseName = databaseName
        self.__tableName = tableName

        self.__mappedTables = []

    def parse(self) -> Database:
        parsedDatabase = Database(self.__databaseName) # creating database object

        # mapping columns in json file
        mappedColumns = list(
            self.__getKeys(
                self.__loadSample()
            )
        )

        # parsing data result to Column type class and adding to database object
        parsedDatabase.addTable(
            self.__createTableFromMappedColumns(
                dataColumns=mappedColumns,
                mainTable=True
            )
        )
        
        # if in the column mapping other tables were found
        if self.__mappedTables:
            while self.__mappedTables:
                mappedTables = self.__mappedTables.copy()
                self.__mappedTables.clear()

                for table in mappedTables:
                    mappedColumns = list(
                        self.__getKeys(table)
                    )

                    parsedDatabase.addTable(
                        self.__createTableFromMappedColumns(
                            dataColumns=mappedColumns,
                            tableName=f"{self.__tableName}.{mappedColumns[0][0].split('.')[0]}"
                        )
                    )

        return parsedDatabase
    
    def __createTableFromMappedColumns(self, dataColumns: list, tableName: str = None, mainTable: bool = False) -> Table:
        return Table(
            tableName if tableName else self.__tableName,
            [Column(field, dtype) for field, dtype in dataColumns],
            mainTable=mainTable
        )

    def __getKeys(self, data, key=[]):
        for k, v in data.items():
            if isinstance(v, dict):
                yield from self.__getKeys(v, key + [k])
            
            elif isinstance(v, list):
                try:
                    if type(v[0]) in (dict, list):
                        self.__mappedTables.append({k:v[0]}) # maps as a new table
                except IndexError:
                    pass
            else:
                yield '.'.join(key + [k]), type(v)

    def __loadSample(self) -> dict:
        with open(self.__sampleFile) as jsonFile:
            return load(jsonFile)

    @property
    def sampleFile(self) -> str:
        return self.__sampleFile
    
    @sampleFile.setter
    def sampleFile(self, sampleFile: str) -> None:
        if isinstance(sampleFile, str):
            self.__sampleFile = sampleFile
        else:
            raise TypeError(f" sampleFile parameter must be a string, {type(sampleFile).__name__} passed.")

    @property
    def databaseName(self) -> str:
        return self.__databaseName
    
    @databaseName.setter
    def databaseName(self, databaseName: str) -> None:
        if isinstance(databaseName, str):
            self.__databaseName = databaseName
        else:
            raise TypeError(f" databaseName parameter must be a string, {type(databaseName).__name__} passed.")

    @property
    def tableName(self) -> str:
        return self.__tableName
    
    @tableName.setter
    def tableName(self, tableName: str) -> None:
        if isinstance(tableName, str):
            self.__tableName = tableName
        else:
            raise TypeError(f" tableName parameter must be a string, {type(tableName).__name__} passed.")