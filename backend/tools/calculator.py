import ast
import operator

class CalculatorTool:
    """
    A simple calculator tool to evaluate mathematical expressions.
    Built securely without using raw eval().
    """
    
    # Supported operators
    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.BitXor: operator.xor,
        ast.USub: operator.neg
    }

    def evaluate_node(self, node):
        """Recursively evaluates the AST node."""
        if isinstance(node, ast.Num): # <number>
            return node.n
        elif isinstance(node, ast.BinOp): # <left> <operator> <right>
            return self.ops[type(node.op)](self.evaluate_node(node.left), self.evaluate_node(node.right))
        elif isinstance(node, ast.UnaryOp): # <operator> <operand> e.g., -1
            return self.ops[type(node.op)](self.evaluate_node(node.operand))
        else:
            raise TypeError(node)

    def calculate(self, expression: str) -> str:
        """
        Evaluates a simple math expression securely.
        """
        print(f"[CalculatorTool] Calculating: {expression}")
        try:
            # Parse the expression into an AST
            node = ast.parse(expression, mode='eval').body
            result = self.evaluate_node(node)
            return str(result)
        except Exception as e:
            return f"Error evaluating expression: {str(e)}"
