class ToolParseMixin:
    has_value_params = ['value_in', 'sim_value_in']
    def _get_tool_params_json(self, tool, table, column, value) -> dict:
        if tool in self.has_value_params:
            return {
                "table": table,
                "column": column,
                "value": value
            }
        else:
            return {
                "table": table,
                "column": column
            }
        

    def _get_tool_string(self, tool, table, column, value) -> str:
        if table == "":
            table = None
        if column == "":
            column = None
        if value == "":
            value = None

        if tool in self.has_value_params:
            return f'{tool}(table={table}, column={column}, value={value})'
        else:
            return f'{tool}(table={table}, column={column})'