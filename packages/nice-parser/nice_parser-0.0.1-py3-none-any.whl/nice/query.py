class Query(object):

    def Save(self, outputName, database):

        with open(outputName, 'w') as file:

            for index, tabela in enumerate(database.table):

                if index == 0:

                        print(f"\n/*{'-' * (len(tabela.name) + 20)}\n  Tabela Principal: {tabela.name.upper()}\n {'-' * (len(tabela.name) + 20)}*/\n", file=file)

                        print(f"SELECT", file=file)

                        for column in tabela.columns:
                            if column != tabela.columns[-1]:
                                print(f'    CAST("json_extract"({tabela.name.split(".")[0]}, \'$.{column.name}\') AS {column.dtype}) "{column.name.replace(".", "_")}",', file=file)
                            else:
                                print(f'    CAST("json_extract"({tabela.name.split(".")[0]}, \'$.{column.name}\') AS {column.dtype}) "{column.name.replace(".", "_")}"', file=file)

                        print(f"FROM {database.name}.{tabela.name.split('.')[0]}", file=file)

                else:
                    print(f"\n/*{'-' * (len(tabela.name) + 20)}\n  Tabela Secundaria: {tabela.name.upper()}\n {'-' * (len(tabela.name) + 20)}*/\n", file=file)

                    print(f"SELECT", file=file)

                    for column in tabela.columns:
                        if column != tabela.columns[-1]:
                            print(f'    CAST("json_extract"("{column.name.split(".")[0]}", \'$.{column.name.split(".")[1]}\') AS {column.dtype}) "{column.name.replace(".", "_")}",', file=file)
                        else:
                            print(f'    CAST("json_extract"("{column.name.split(".")[0]}", \'$.{column.name.split(".")[1]}\') AS {column.dtype}) "{column.name.replace(".", "_")}"', file=file)

                    print(f'FROM ({database.name}.{tabela.name.split(".")[0]} v CROSS JOIN UNNEST(CAST("json_extract"("v"."{tabela.name.split(".")[0]}", \'$.{column.name.split(".")[0]}\') AS array(json))) t ({column.name.split(".")[0]})) ', file=file)