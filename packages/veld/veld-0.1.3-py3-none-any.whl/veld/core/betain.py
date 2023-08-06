# -*- coding: utf-8 -*-

import math


def betain(x, p, q, tol=1e-15):
    """Beta distribution function

    This function implements the algorithm for the incomplete beta integral by
    Martin Newby (see [1]). The integral is defined as:

        I_x(p, q) = 1/B(p, q) \int_{0, x} u^{p - 1} (1 - u)^{q - 1} du

    with 0 <= x <= 1, p > 0, and q > 0.

    Parameters
    ----------
    x : float
        upper limit of the incomplete beta integral

    p : float
        First parameter for the incomplete beta integral

    q : float
        Second parameter for the incomplete beta integral

    tol : float
        Tolerance for the numerical approximation of the integral

    Returns
    -------
    float
        Estimated value of the incomplete beta integral

    [1]: Newby, M.J. (1991) The incomplete beta integral (TH Eindhoven.
    THE/BDK/ORS, Vakgroep ORS: rapporten; Vol. 9106). Technische Universiteit
    Eindhoven.

    """

    # Check the parameters: x in [0, 1] and p and q > 0
    if p <= 0 or q <= 0:
        raise ValueError("Both p and q must be larger than 0.")

    output = x
    w = x
    pplusq = p + q

    if w < 0 or w > 1:
        raise ValueError("x must be in [0, 1]")
    # The simple special cases when one of p or q is 1 or x is 0 or 1.
    elif w == 0 or w == 1:
        pass
    elif q == 1:
        output = w**p
    elif p == 1:
        output = 1 - (1 - w) ** q
    # Now use the expansions from Abramowitz & Stegun, choose the best tail
    elif p > w * pplusq:
        b = math.lgamma(p) + math.lgamma(q) - math.lgamma(pplusq)
        output = beta0(w, p, q, b, tol)
    else:
        b = math.lgamma(p) + math.lgamma(q) - math.lgamma(pplusq)
        output = 1 - beta0(1 - w, q, p, b, tol)
    return output


def beta0(x, p, q, b, tol):
    """Beta distribution function

    Uses the series expansions from Abramowitz & Stegun, results 26.5.4 and
    26.5.5.

    This is the internal function that implements the approximation. It
    performs no argument checking. Users should use the :func:`betain` function
    instead.

    """
    u = x
    cu = 1 - u

    # Use logarithms to reduce chance of overflow
    a0 = p * math.log(u) + (q - 1) * math.log(cu) - math.log(p) - b
    s0 = 1
    t0 = 1
    pplusq = p + q
    ns = int(q + cu * pplusq)

    # Expansion 26.5.5 from Abramowitz and Stegun
    #
    # Even if NS=0 at least one reduction gets correctly done because the loop
    # does not execute in strict fortran 77.
    # NOTE: Also not in Python.
    ca = q - 1
    cb = p + 1
    r = u / cu

    for i in range(ns):
        t0 = t0 * r * ca / cb
        s0 = s0 + t0
        ca = ca - 1
        cb = cb + 1

    # Correction term for expansion 26.5.4
    t0 = t0 * u * ca / cb
    ca = pplusq
    cb = cb + 1
    check = abs(t0)

    # Expansion 26.5.4 expressed as a while loop
    while not (check <= tol and check <= tol * abs(s0)):
        s0 = s0 + t0
        t0 = t0 * u * ca / cb
        ca = ca + 1
        cb = cb + 1
        check = abs(t0)

    return math.exp(a0) * s0
