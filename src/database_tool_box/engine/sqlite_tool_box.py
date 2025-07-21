from .base_db_tool_box import DatabaseToolBox
import sqlite3
import random
import re

class SqliteToolBox(DatabaseToolBox):
    def __init__(self, db_file, config_file="./config/db_tool_box.json"):
        super().__init__(db_file, config_file=config_file)
        
    def connect(self):
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        
    def close(self):
        self.conn.close()

    def sqlite_clean_db_schema(self):
        if self.clean_db_schema is None:
            self.cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
            schema = self.cursor.fetchall()

            schema_text = ""
            for table in schema:
                schema_text += table[0]

            # delete comments, \n, spaces
            schema_text = re.sub(r'--.*,', '', schema_text)
            schema_text = re.sub(r'\n', '', schema_text)
            schema_text = re.sub(r' +', ' ', schema_text)
            self.clean_db_schema = schema_text

        return self.clean_db_schema
    
    def get_column_list(self):
        if self.column_list is None:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = self.cursor.fetchall()
            tables = [table[0] for table in tables if table[0] != 'sqlite_sequence']

            self.column_list = {}
            for table in tables:
                self.column_list[table] = []
                self.cursor.execute(f"PRAGMA table_info({table})")
                columns = self.cursor.fetchall()
                for column in columns:
                    self.column_list[table].append(column[1])

        return self.column_list
    

    def fetch_n(self, table, column, n=-1, mode='normal', buffer_size=None):
        """
        parameters:
            - table, column: fetch data from table.column
            - n: number of records to fetch. Set to -1 to fetch all records.
            - mode: 'normal' or 'distinct'. If 'distinct', the fetched data will be distinct.
            - buffer_size: The maximum number of values to fetch. Set to None to fetch all values in a column at most, when the database is very large, there may be out of memory.
        """
        if mode == 'distinct':
            self.cursor.execute(f"SELECT DISTINCT `{column}` FROM `{table}`")
        else:
            self.cursor.execute(f"SELECT `{column}` FROM `{table}`")

        if buffer_size is None and n == -1:
            return self.cursor.fetchall()
        if n == -1:
            n = buffer_size
        elif buffer_size is not None:
            n = min(n, buffer_size)
        return self.cursor.fetchmany(n)
    

    def fetch_equal(self, table, column, value, buffer_size=None):
        """
        parameters:
            - table, column, value: fetch data from table.column where column == value
            - buffer_size: The maximum number of data to fetch. Set to None to fetch all values in a column at most, when the database is very large, there may be out of memory.
        """
        if value == 'null':
            self.cursor.execute(f"SELECT `{column}` FROM `{table}` WHERE `{column}` is null")
        else:
            self.cursor.execute(f"SELECT `{column}` FROM `{table}` WHERE `{column}` == '{value}'")

        if buffer_size is None:
            return self.cursor.fetchall()
        else:
            return self.cursor.fetchmany(buffer_size)