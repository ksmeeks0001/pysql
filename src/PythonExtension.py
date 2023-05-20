from jinja2.ext import Extension
from jinja2 import nodes


class PythonExtension(Extension):
    """
    Jinja Extension to execute Python code
    updates the template context with anything defined
    """
    tags = {'python',}

    def __init__(self, environment):
        super().__init__(environment)
    
    def parse(self, parser):
        """
        A python tag should not contain any other tags
        only python code
        """
        lineno = parser.stream.expect('name:python').lineno

        # get the expression inside the tag
        body = parser.parse_statements(['name:endpython'], drop_needle=True)
        code = body[0].nodes[0].data
        return self._python(code)
        
    def _python(self, code):

        new_nodes = []
             
        # evaluate the code and return the output
        exec(code.strip(), self.environment.python_execution_context)
           
        for key, value in self.environment.python_execution_context.items():
            if key == ('__builtins__'):
                continue

            converted_value = self.environment.jinja_convert_type(value)
                              
            new_node = nodes.Assign(
                nodes.Name(key, 'store'),
                nodes.Const(converted_value)
                )
            new_nodes.append(new_node)
            
        return new_nodes

        