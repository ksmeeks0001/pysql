import os
from copy import deepcopy

from jinja2.ext import Extension
from jinja2 import nodes
from sqlalchemy import create_engine, text


class SQLExtension(Extension):
    """
        Jinja Extension to execute SQL 
        adding a list of the resulting rows to the template context
    """
    tags = {'sql',}

    def __init__(self, environment):
        super().__init__(environment)
    
    def parse(self, parser):
        """
        
        """
        lineno = next(parser.stream).lineno

        variable = parser.parse_expression()
        
        body = parser.parse_statements(['name:endsql'], drop_needle=True)
        code = body[0].nodes[0].data
        
        result = self._sql(code)
        self.environment.python_execution_context[variable.name] = result
        converted_result = self.environment.jinja_convert_type(deepcopy(result))
        
        return [
            nodes.Assign(
                nodes.Name(variable.name, 'store'),
                nodes.Const(converted_result)
                )
            ]

    
    def _sql(self, code):
    
        connstring = os.environ.get('PYSQL_DB_CONN_STRING', None)
        if connstring is None:
            raise Exception("Environment variable PYSQL_DB_CONN_STRING must be defined to use the SQL extension")
        
        engine = create_engine(connstring)
        with engine.connect() as connection:
            return [x._asdict() for x in connection.execute(text(code))]

