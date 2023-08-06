#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def set_precision(number: float | str,
                  precision: int | str = 1) -> str | Exception:
    """Returns a string representation of a :param:`number` formatted to the given precision of :param:`precision` significant figures.

    Example:

    ```python
    >>> from SetPrecision import set_precision
    >>> decimal = set_precision(number=3.1459, precision=2)
    >>> print(decimal)
    '3.15'
    ```

    ---

    :param number: float/decimal to be formatted. Will attempt to convert strings to floats
    :type number: :class:`float` | :class:`str`
    :param precision: number of decimal places to which :param:`number` is set to contain. Will attempt to convert strings to integers, defaults to 1
    :type precision: :class:`int` | :class:`str`, optional
    :return: final string representation of formatted float/decimal :param:`number`
    :rtype: :class:`str`
    """
    try:
        number = float(number)
        precision = int(precision)

        return f"{number:.{precision}f}"

    except Exception as exc:
        return exc