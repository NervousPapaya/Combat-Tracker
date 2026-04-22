import operator

def is_whole_number(x):
    return isinstance(x, int) or (isinstance(x, float) and x.is_integer())

#Setting up a save evaluation function.
# This ensures that users cannot run code in the evaluation cells
def safe_eval(expr):
    ops = {'+': operator.add, '-': operator.sub, '*': operator.mul, '/': operator.truediv}
    for op in ops:
        if op in expr:
            left, right = expr.split(op)
            return int(ops[op](int(left), int(right)))
    return expr #Returns expression if nothing matches