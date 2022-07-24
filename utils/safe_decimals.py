from decimal import Decimal
from math import isclose


def dec(val) -> Decimal:
    if isinstance(val, float):
        raise ArithmeticError
    return Decimal(val)


def leq(val1, val2) -> bool:
    """if val1 is less than val2 or is close enough"""
    return val1 < val2 or isclose(val1, val2)


def geq(val1, val2) -> bool:
    """if val1 is greater than val2 or is close enough"""
    return val1 > val2 or isclose(val1, val2)


def gt(val1, val2) -> bool:
    """if val1 >= val2 and val1 is not close to val2"""
    return not leq(val1, val2)


def lt(val1, val2) -> bool:
    """if val1 <= val2 and val1 is not close to val2"""
    return not geq(val1, val2)


# def less(val1, val2) -> bool:
#     # false if val1 and val2 are not close and val1 >= val2
#     return not isclose(val1, val2) and val1 < val2
#
#
# def greater(val1, val2) -> bool:
#     # false if val1 and val2 are not close and val1 <= val2
#     return isclose(val1, val2) and val1 > val2
