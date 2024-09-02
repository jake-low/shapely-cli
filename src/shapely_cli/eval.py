from shapely import *
from .helpers import geodesic_length, geodesic_area, geodesic_perimeter, proj

def evaluate(expr, locals):
    def __exec_with_return(code: str, globals: dict, locals: dict):
        import ast

        a = ast.parse(code)
        last_expression = None
        if a.body:
            if isinstance(a.body[-1], ast.Expr):
                last_expression = ast.unparse(a.body.pop())
        
        exec(ast.unparse(a), globals, locals)

        if last_expression:
            retval = eval(last_expression, globals, locals)
            return (True, retval)
        else:
            return (False, None)

    return __exec_with_return(expr, globals(), locals)

