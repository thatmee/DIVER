from .engine import SqliteToolBox
import pandas as pd
import os
from logging import getLogger

logger = getLogger(__name__)

class BirdToolBox(SqliteToolBox):
    def debug(self, attribute):
        eval(f"print(self.{attribute})")

    def get_basic_info(self):
        return self.sqlite_clean_db_schema()
    
    
    def get_columns_and_descriptions(self):
        if self.column_desp is None:
            self.column_desp = {}
            logger.info('Call get_column_description for the first time. Read in the description information.')
            # find all tables
            table_columns = self.get_column_list()
            tables = table_columns.keys()
            
            data_dir = '/'.join(self.db_file.split('/')[:-1])
            desc_dir = data_dir + '/database_description'

            for table in tables:
                desc_path = f'{desc_dir}/{table}.csv'
                if not os.path.exists(desc_path):
                    continue
                try:
                    desc = pd.read_csv(desc_path)
                except Exception as e:
                    logger.error(f"Error reading {desc_path}: {e}. Skipping this file.")
                    self.column_desp[table] = {}
                    continue
                desc['original_column_name'] = desc['original_column_name'].str.strip()
                desc['column_description'] = desc['column_description'].fillna('')
                desc['value_description'] = desc['value_description'].fillna('')
                desc['description'] = table + '.' + desc['original_column_name'] + ': ' + desc['column_description'] + '. ' + desc['value_description']
                self.column_desp[table] = pd.Series(desc['description'].values, index=desc['original_column_name'].values).to_dict()

        return self.column_desp