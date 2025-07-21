import random
import traceback
from abc import ABC, abstractmethod
from src.utils import SimilarityMixin, ConfigManageMixin
from .tool_parse_mixin import ToolParseMixin


suggestion_start = "This lookup has been called before and the results remain the same. "
suggestions = {
    "value_in": suggestion_start + "You may want to find similar values with 'sim_value_in'.",
    "sim_value_in": suggestion_start + "If the expected value is not found, try using 'sim_columns' to find related columns and lookup them. Use 'none' to skip lookup if there is nothing else to lookup.",
    "uniq_value": suggestion_start + "If unique values are truncated, 'sim_value_in' should be tried to find similar values more specifically. If unique values are not truncated and the expected value is still not found, try to lookup other related columns.",
    "head": suggestion_start + "You may want to get a more comprehensive view of what data is in this column with 'uniq_value' or to check a specific value and its similar values with 'value_in' or 'sim_value_in'.",
    "random": suggestion_start + "You may want to get a more comprehensive view of what data is in this column with 'uniq_value' or to check a specific value and its similar values with 'value_in' or 'sim_value_in'.",
    "if_null": suggestion_start + "Use 'none' to skip lookup if there is nothing else to lookup."
}
# suggestions = {
#     "value_in": suggestion_start,
#     "sim_value_in": suggestion_start,
#     "uniq_value": suggestion_start,
#     "head": suggestion_start,
#     "random": suggestion_start,
#     "if_null": suggestion_start
# }


class DatabaseToolBox(ABC, SimilarityMixin, ConfigManageMixin, ToolParseMixin):
    def __init__(self, db_file, config_file):
        self.db_file = db_file
        self.config_file = config_file
        self.connect()
        self.clean_db_schema = None
        self.add_config_names(['head_random_n', 'unique_n', 'sim_top_n'])
        self.load_config(config_file=config_file)
        self.column_desp = None
        self.column_list = None

    def __del__(self):
        self.close()

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def get_basic_info(self):
        """get basic info to feed to model. Different dataset has different scale of database, so this method should be implemented in the subclass. For smaller database, basic info can be the schema of the database. For larger database, basic info can be the list of tables."""
        pass

    @abstractmethod
    def get_column_list(self):
        """
        get all columns in the database.
        format: list[str], [table1.column1, table1.column2, ...]
        """
        pass

    @abstractmethod
    def get_columns_and_descriptions(self) -> dict:
        """different dataset provide description or evidence in different format, so this method should be implemented in the subclass"""
        pass

    @abstractmethod
    def fetch_n(self, table, column, n=-1, mode='normal', buffer_size=None):
        """
        parameters:
            - table, column: fetch data from table.column
            - n: number of records to fetch. Set to -1 to fetch all records.
            - mode: 'normal' or 'distinct'. If 'distinct', the fetched data will be distinct.
            - buffer_size: The maximum number of values to fetch. Set to None to fetch all values in a column at most, when the database is very large, there may be out of memory.
        """
        pass
    
    @abstractmethod
    def fetch_equal(self, table, column, value, buffer_size=None):
        """
        parameters:
            - table, column, value: fetch data from table.column where column == value
            - buffer_size: The maximum number of data to fetch. Set to None to fetch all values in a column at most, when the database is very large, there may be out of memory.
        """
        pass


    def value_in(self, table, column, value):
        equal_value_list = self.fetch_equal(table, column, value)
        return len(equal_value_list) > 0


    def sim_value_in(self, table, column, value):
        value_list = self.fetch_n(table, column, mode='distinct', n=-1)
        value_list = [v[0] for v in value_list]
        topn_sim = self.bert_similarity(value, value_list, topn=self.sim_top_n)
        return {
            f"top_{self.sim_top_n}_similarity_text_score": topn_sim
        }


    def sim_columns(self, table, column):
        all_columns_desc = self.get_columns_and_descriptions()

        if table not in self.column_list.keys():
            raise ValueError(f"table {table} not in the database")
        if column not in self.column_list[table]:
            raise ValueError(f"column {column} not in the table {table}")
        
        key_column_w_desp, column_list_w_desp = [], []
        for t, columns_desc in all_columns_desc.items():
            for c, desc in columns_desc.items():
                if t == table and c == column:
                    key_column_w_desp.append(desc)
                else:
                    column_list_w_desp.append(desc)
        
        if len(key_column_w_desp) == 0:
            key_column_w_desp = f"{table}.{column}: no description"

        topn_sim = self.bert_similarity(key_column_w_desp, column_list_w_desp, topn=self.sim_top_n)
        return {
            f"top_{self.sim_top_n}_similarity_text_score": topn_sim
        }
    

    def info(self, table, column):
        all_column_desc = self.get_columns_and_descriptions()
        if table not in self.column_list.keys():
            raise ValueError(f"table {table} not in the database")
        if column not in self.column_list[table]:
            raise ValueError(f"column {column} not in the table {table}")
        
        description = all_column_desc.get(table, {}).get(column, None)
        return description


    def uniq_value(self, table, column):
        value_list = self.fetch_n(table, column, mode='distinct', buffer_size=505)
        unique_values_count = len(value_list)
        
        if unique_values_count > 500:
            unique_values_count_str = f"more than 500, only show {self.unique_n} values below"
        elif unique_values_count > self.unique_n:
            unique_values_count_str = f"{unique_values_count}, only show {self.unique_n} values below"
        else:
            unique_values_count_str = f"{unique_values_count}, show all values below"

        value_list = value_list[:self.unique_n]
        
        return {
            "total number of unique values": unique_values_count_str,
            "values": value_list
        }


    def head(self, table, column):
        value_list = self.fetch_n(table, column, n=self.head_random_n)
        return value_list


    def random(self, table, column):
        value_list = self.fetch_n(table, column)
        random_10 = random.sample(value_list, self.head_random_n)
        return random_10
    

    def if_null(self, table, column):
        value_list = self.fetch_equal(table, column, 'null')
        if len(value_list) > 0:
            return "there are null in this column"
        else:
            return "null dose not exist in this column"
    
            
    def execute_tool(self, tool, tool_params):
        tool_result = eval(f"self.{tool}")(**tool_params)
        return tool_result
    

    def execute_lookups(self, response, history_tool_chain):
        """
        Lookup the database with the tools.
        Return the results of lookups.
        """
        continue_lookup = False
        return_dict = {}

        for phrase, thought in response.items():
            return_dict[phrase] = []
            called_set = history_tool_chain[phrase]['set']
            for lookup in thought['lookup']:
                tool = lookup['lookup_type']
                tool_params = {
                    "table": lookup['lookup_table'],
                    "column": lookup['lookup_column']
                }

                if tool in ['value_in', 'sim_value_in']:
                    tool_params['value'] = lookup['lookup_value']

                if tool != 'none':
                    continue_lookup = True

                    # check if the same tool has been called before
                    tool_str = self._get_tool_string(
                        tool, tool_params['table'], 
                        tool_params['column'], 
                        tool_params.get('value', None)
                    )
                    if tool_str in called_set:
                        return_dict[phrase].append({
                            "tool": tool,
                            "params": tool_params,
                            "result": suggestions[tool]
                        })
                        continue

                    try:
                        tool_result = self.execute_tool(tool, tool_params=tool_params)
                    except Exception as e:
                        tool_result = f"Error in calling this tool: {e}. Please carefully check the table name, column name and value you provided."
                        print("An error in calling tool has been feedback to the agent: ", e)
                        traceback.print_exc()

                    return_dict[phrase].append({
                        "tool": tool,
                        "params": tool_params,
                        "result": tool_result
                    })
                    continue

                if tool_params['table'] != "" or tool_params['column'] != "":
                    continue_lookup = True
                    tool_result = "You choose the tool 'none', but the table or column is not empty. If you are sure to skip this lookup, please clear the table and column."
                else:
                    tool_result = None

                return_dict[phrase].append({
                    "tool": tool,
                    "params": tool_params,
                    "result": tool_result
                })

        return return_dict, continue_lookup