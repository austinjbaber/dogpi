"""Helpers for number manipulation"""
import numbers
import math

__all__ = ["try_round"]


def try_round(num: numbers.Real) -> int | None:
        if not isinstance(num, numbers.Real):
            return None
        # floor(num + .5) is used here because round() does bankers rounding by rounding to the nearest EVEN integer. 4.5 -> 4, 5.5 -> 6
        return math.floor(num + .5)