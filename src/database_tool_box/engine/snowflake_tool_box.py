from .base_db_tool_box import DatabaseToolBox
import sqlite3
import snowflake.connector
import os
import random
import re
import json
import pandas as pd


class SnowflakeToolBox(DatabaseToolBox):
    def __init__(self, db_file, config_file="./config/db_tool_box.json", credential_file='/{PATH_TO_DIVER_PROJECT}/DIVER/config/credentials/snowflake_credential.json'):
        self.credential_file = credential_file
        super().__init__(db_file, config_file=config_file)
        
    def connect(self):
        # Load Snowflake credentials
        snowflake_credential = json.load(open(self.credential_file))

        # Connect to Snowflake
        self.conn = snowflake.connector.connect(
            **snowflake_credential
        )
        self.cursor = self.conn.cursor()

        # Set the database and schema
        self.cursor.execute(f"USE DATABASE {self.db_name}")
        # self.cursor.execute(f"USE SCHEMA {self.schema_name}")

        
    def close(self):
        self.cursor.close()
        self.conn.close()
        

    def get_tables_of_schema(self, schema):
        self.cursor.execute(f"SHOW TABLES IN SCHEMA {schema}")
        results = self.cursor.fetchall()
        tables = [item[1] for item in results]
        return tables
    
    
    def get_columns_of_table(self, schema, table):
        self.cursor.execute(f"SHOW COLUMNS IN TABLE {schema}.{table}")
        results = self.cursor.fetchall()
        columns = [item[2] for item in results]
        return columns
    

    def fetch_n(self, table, column, n=-1, mode='normal', buffer_size=None):
        """
        parameters:
            - table, column: fetch data from table.column
            - n: number of records to fetch. Set to -1 to fetch all records.
            - mode: 'normal' or 'distinct'. If 'distinct', the fetched data will be distinct.
            - buffer_size: The maximum number of values to fetch. Set to None to fetch all values in a column at most, when the database is very large, there may be out of memory.
        """
        if mode == 'distinct':
            self.cursor.execute(f"SELECT DISTINCT {column} FROM {table}")
        else:
            self.cursor.execute(f"SELECT {column} FROM {table}")

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
            self.cursor.execute(f"SELECT {column} FROM {table} WHERE {column} is null")
        else:
            self.cursor.execute(f"SELECT {column} FROM {table} WHERE {column} == '{value}'")

        if buffer_size is None:
            return self.cursor.fetchall()
        else:
            return self.cursor.fetchmany(buffer_size)