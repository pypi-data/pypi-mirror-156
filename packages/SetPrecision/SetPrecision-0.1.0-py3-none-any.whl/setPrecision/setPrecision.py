#!/usr/bin/env python3


def set(digit: float | str, precision: int | str = 1) -> str:
    """Returns a string representation of a number `digit` formatted to the given precision of `precision` significant digits.

    Example:

    ```python
    >>> from setPrecision import set
    >>> num = 3.1459 # Not necessary to set number as variable.
    >>> num = set(digit = num, precision = 2)
    >>> print(num)
    '3.15'
    ```

    ---
    Parameters
        :param digit: Float/decimal to be formatted. Will attempt to convert strings to floats.
        :type digit: float | str
        :param precision: number of decimal places to which `digit` is set to contain. Will attempt to convert strings to integers, defaults to 1.
        :type precision: int | str
        :return: final string representation of formatted float/decimal `digit`.
        :rtype: str
    """
    try:
        digit = float(digit)
        precision = int(precision)
        return f"{digit:.{precision}f}"
    except Exception as exc:
        return f"Error occurred during method execution...\n\nException Message:\n==> {exc}\n"