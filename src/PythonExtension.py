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
        
        if len(body[0].nodes) > 1:
            raise Exception("Inner nodes not allowed within python tags")

        code = body[0].nodes[0].data
        return self._python(code)
        
    def _python(self, code):

        new_nodes = []
             
        # evaluate the code and update the context
        exec(code.strip(), self.environment.python_execution_context)        
        self.environment.globals.update(self.environment.python_execution_context) 
            
        return []

        