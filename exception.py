class MissingColumnError(Exception):
    '''This Exception Class is used to raise error when uploaded
       file doesnt contains any column
    '''
    def __init__(self, column_name,file):
        self.column_name = str(column_name)[1:-1]
        self.file = file

    def __str__(self):
        return f"'{self.column_name}' Columns missing in '{self.file}' dataset."

class DataNotAvailable(Exception):
    '''This Exception Class is used to raise error when Selected order has no records.
    '''
    def __init__(self):
        self.msg = 'Data Not Found.'

    def __str__(self):
        return f"Selected order has no data."
