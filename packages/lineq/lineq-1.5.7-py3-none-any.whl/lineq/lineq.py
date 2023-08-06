import numpy as np
from numpy.typing import ArrayLike


def equation(x : ArrayLike, y : ArrayLike, symbol = 'x', decimal = 2) -> str:
    """This function, returns the equation of the linear fitted curve!
    
    **params:
        x : must be ArrayLike.
        y : must be ArrayLike.
        symbol : default is 'x'. specifies the symbol!.
            example:
                if symbol is 'x':
                    y = 0.19x + 10.46
        decimal: specifies the decimal of x and y. default is 2.
            example:
                if decimal is 3, the output is like this:
                    y = 0.194x + 10.463
    """
    slope, intercept = np.polyfit(x, y, 1)
    eq = f"y = {round(slope, decimal)}{symbol} + {round(intercept, decimal)}"
    return eq