import ast
import operator

def is_whole_number(x):
    return isinstance(x, int) or (isinstance(x, float) and x.is_integer())

#Setting up a safe evaluation function.
# This ensures that users cannot run code in the evaluation cells
#First we set up a dictionary for translating operations.
#This dictionary dictates what operations are legal.
#NOTE: Division is handled as floor division as most DnD divisions round down
OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.floordiv,
    ast.UAdd: operator.pos,
    ast.USub: operator.neg
}

def safe_eval(expr: str):
    node = ast.parse(expr, mode="eval")

    def _eval(nod): #defining a helper function
        # if the node is just a single constant, we return the value.
        # We raise an error if the value is not a number
        if isinstance(nod, ast.Constant):
            if isinstance(nod.value, int):
                return nod.value
            raise ValueError("Only integers allowed")

        # Binary operations are handled here
        if isinstance(nod, ast.BinOp):
            left = _eval(nod.left)
            right = _eval(nod.right)
            op_type = type(nod.op)

            if op_type not in OPS:
                raise ValueError(f"Operator not allowed: {op_type}")
            return OPS[op_type](left,right)  # Finds the operator corresponding to ast operation and then applies it

        #Handling unary operations such as +3 or -5
        if isinstance(nod, ast.UnaryOp):
            op_type = type(nod.op)
            if op_type not in OPS:
                raise ValueError(f"Operator not allowed: {op_type}")
            return OPS[op_type](_eval(nod.operand))

        raise ValueError("Unsupported expression")

    try:
        result = _eval(node.body)
    except ZeroDivisionError:
        raise ValueError("Division by zero is not allowed")
    return int(result)



# def safe_eval(expr: str):
#     ops = {'+': operator.add, '-': operator.sub, '*': operator.mul, '/': operator.truediv}
#     for op in ops:
#         if op in expr:
#             left, right = expr.split(op)
#             return int(ops[op](int(left), int(right)))
#     return expr #Returns expression if nothing matches