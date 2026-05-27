"""Try alternative initialisations of the parallel reduction for T_c.

Variant A (in count_obstructions_generic.py): m := (r - sigma)/2^v with sigma = -sign(c),
that is m := (r + sign(c))/2^v.  This is the natural extension of the manuscript convention.

Variant B (this script): m := (r + c)/2^v with v := v_2(r + c).  This is the
"scaled" convention that may be more natural for |c| > 1.

Variant C: m := (r - c)/2^v with v := v_2(r - c).
"""

import sys
from fractions import Fraction


def v2(n):
    if n == 0:
        return 10**9
    n = abs(n)
    c = 0
    while (n & 1) == 0:
        n >>= 1
        c += 1
    return c


def parallel_reduce_variantB(r, L, c, a=3):
    """m := (r + c)/2^v with v := v_2(r + c), for the map T_{a,c} (a odd).

    Initial affine: a_I = c_0 * a_K + d_0 with c_0 = 2^{-v} and d_0 = c * 2^{-v}.
    The multiplier defaults to a=3 (the Collatz/3n+c case); pass a explicitly
    for the general (an+c) family.
    """
    if r % 2 == 0 or c == 0 or c % 2 == 0 or a % 2 == 0:
        return None
    if r + c == 0:
        return None
    v = v2(r + c)
    if v <= 0 or v >= L:
        return None
    factor = 1 << v
    m = (r + c) // factor
    if m % 2 == 0:  # m must be odd
        return None
    a_K, b_K = r, 1 << L
    a_I, b_I = m, 1 << (L - v)
    coef = Fraction(1, factor)
    dval = Fraction(c, factor)

    V_K = 0
    V_I = 0
    while True:
        A_K = a * a_K + c
        v_K = v2(A_K)
        v_b_K = v2(b_K)
        A_I = a * a_I + c
        v_I = v2(A_I)
        v_b_I = v2(b_I)

        if v_K >= v_b_K or v_I >= v_b_I:
            return (coef, dval, V_K, V_I, v)

        coef_old = coef
        coef = coef_old * Fraction(1 << v_K, 1 << v_I)
        dval = (a * dval + c * (1 - coef_old)) / Fraction(1 << v_I)
        a_K = A_K >> v_K
        b_K = (a * b_K) >> v_K
        a_I = A_I >> v_I
        b_I = (a * b_I) >> v_I
        V_K += v_K
        V_I += v_I


def is_obstr_B(endpoint, c, a=3):
    """For variant B, obstruction means Phi_J = c(1 - c_J) + a d_J = 0."""
    if endpoint is None:
        return False
    coef, dval, _, _, _ = endpoint
    return c * (1 - coef) + a * dval == 0


def count_B(L, c, a=3):
    obstr = []
    for r in range(1, 1 << L, 2):
        ep = parallel_reduce_variantB(r, L, c, a)
        if is_obstr_B(ep, c, a):
            obstr.append(r)
    return len(obstr), obstr


def main():
    print("# Variant B: m := (r + c)/2^v")
    print()
    print("c | L=6 | L=8 | L=10 | L=12 | L=14")
    print("---|---|---|---|---|---")
    for c in [-13, -11, -9, -7, -5, -3, -1, 1, 3, 5, 7, 9, 11, 13]:
        row = [f"{c:+d}"]
        for L in [6, 8, 10, 12, 14]:
            total, _ = count_B(L, c)
            row.append(str(total))
        print(" | ".join(row))


if __name__ == "__main__":
    main()
