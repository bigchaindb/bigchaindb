class Schema:

    def create_database(self):
        raise NotImplementedError()

    def create_tables(self):
        raise NotImplementedError()

    def create_indexes(self):
        raise NotImplementedError()

    def drop_database(self):
        raise NotImplementedError()
