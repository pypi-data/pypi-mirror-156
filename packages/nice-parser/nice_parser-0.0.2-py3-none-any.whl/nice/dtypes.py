class DType:
    types = {
        str: 'VARCHAR',
        bool: 'BOOLEAN',
        int: 'BIGINT',
        float: 'DECIMAL'
    }

    @staticmethod
    def getTypeOf(dtype: type) -> str:
        _dtype = __class__.types.get(dtype)

        if not _dtype:
            raise Exception(f" {dtype} not mapped.\n Mapped types: {__class__.getMappedTypes()}")

        return _dtype

    @staticmethod
    def getMappedTypes():
        return __class__.types