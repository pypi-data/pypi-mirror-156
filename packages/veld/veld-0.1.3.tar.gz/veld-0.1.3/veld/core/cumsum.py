# -*- coding: utf-8 -*-

from typing import List


def cumsum(x: List[float]) -> List[float]:
    if not x:
        return []
    y = []  # type: List[float]
    for i, val in enumerate(x):
        prev = 0 if len(y) == 0 else y[-1]
        y.append(prev + val)
    return y
