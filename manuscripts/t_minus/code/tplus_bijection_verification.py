"""Empirical verification of Lemma 7.1 (T- / T+ bijection).

The manuscript claims that the involution r -> bar{r} := (-r) mod 2^L maps the
T_-(n) = (3n-1)/2^{v_2(3n-1)} parallel reduction at (r, L) to the
T_+(n) = (3n+1)/2^{v_2(3n+1)} parallel reduction at (bar{r}, L), with
matching 2-adic valuations at every step and terminal data related by
(c^+_J, d^+_J) = (c^-_J, -d^-_J). The X-criterion 3d + c = 1 on the T-
side is therefore equivalent to c - 3d = 1 (equivalently, 3d^+ + c^+ = 1
read with the sign-flipped d) on the T+ side, giving the bijection
Obstr_L ↔ Obstr^+_L.

We verify the stepwise identity directly by running both reductions
in parallel and comparing valuation sequences and terminal data.

Run with optional level argument; default L = 12.
Runtime: O(L * 2^L); ~1s at L = 12, a few seconds at L = 14.
"""

from __future__ import annotations
import sys
from fractions import Fraction


def v2(n):
    if n == 0:
        return -1
    n = abs(n)
    c = 0
    while (n & 1) == 0:
        n >>= 1
        c += 1
    return c


def step_T_minus(a, b):
    A = 3 * a - 1
    v_a = v2(A)
    v_b = v2(b) if b != 0 else 10**9
    if v_a >= v_b:
        return None, v_a
    return (A // (1 << v_a), (3 * b) // (1 << v_a)), v_a


def step_T_plus(a, b):
    A = 3 * a + 1
    v_a = v2(A)
    v_b = v2(b) if b != 0 else 10**9
    if v_a >= v_b:
        return None, v_a
    return (A // (1 << v_a), (3 * b) // (1 << v_a)), v_a


def reduce_T_minus(r, L):
    """Run T- parallel reduction at (r, L). Return terminal (c, d), valuation
    sequences, and terminal X = 3d + c. Returns None if r is not a valid start
    (r even, or v_2(r-1) outside (0, L))."""
    if r % 2 == 0:
        return None
    v = v2(r - 1)
    if v <= 0 or v >= L:
        return None
    factor = 1 << v
    m = (r - 1) // factor
    a_K, b_K = r, 1 << L
    a_I, b_I = m, 1 << (L - v)
    c = Fraction(1, factor)
    d = Fraction(-1, factor)
    vK_seq, vI_seq = [], []
    while True:
        step_K, vK = step_T_minus(a_K, b_K)
        step_I, vI = step_T_minus(a_I, b_I)
        if step_K is None or step_I is None:
            break
        vK_seq.append(vK)
        vI_seq.append(vI)
        c_old = c
        c = c_old * Fraction(1 << vK, 1 << vI)
        d = (3 * d + c_old - 1) / Fraction(1 << vI)
        a_K, b_K = step_K
        a_I, b_I = step_I
    return c, d, 3 * d + c, vK_seq, vI_seq


def reduce_T_plus(rbar, L):
    """Run T+ parallel reduction at (bar{r}, L). The initial affine relation
    is a_I = 2^{-v} a_K + 2^{-v} with v = v_2(bar{r}+1), m̄ = (bar{r}+1)/2^v.
    Update rule: d_{j+1} = (3 d_j - c_j + 1) / 2^{v_I^{(j)}}, c_{j+1} as for T-.
    Returns terminal (c, d), valuation sequences, and X^+ := c - 3d (which is
    1 iff the involution image is an obstruction of T-)."""
    if rbar % 2 == 0:
        return None
    v = v2(rbar + 1)
    if v <= 0 or v >= L:
        return None
    factor = 1 << v
    mbar = (rbar + 1) // factor
    a_K, b_K = rbar, 1 << L
    a_I, b_I = mbar, 1 << (L - v)
    c = Fraction(1, factor)
    d = Fraction(1, factor)
    vK_seq, vI_seq = [], []
    while True:
        step_K, vK = step_T_plus(a_K, b_K)
        step_I, vI = step_T_plus(a_I, b_I)
        if step_K is None or step_I is None:
            break
        vK_seq.append(vK)
        vI_seq.append(vI)
        c_old = c
        c = c_old * Fraction(1 << vK, 1 << vI)
        d = (3 * d - c_old + 1) / Fraction(1 << vI)
        a_K, b_K = step_K
        a_I, b_I = step_I
    return c, d, c - 3 * d, vK_seq, vI_seq


def main():
    L = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    print(f"Lemma 7.1 (T- / T+ bijection) verification at L = {L}\n")

    minus_count = 0
    plus_count = 0
    obstr_minus = set()
    obstr_plus = set()
    mismatches = []
    valuation_mismatches = []
    pairs_checked = 0

    for r in range(1, 1 << L, 2):
        res_minus = reduce_T_minus(r, L)
        if res_minus is None:
            continue
        rbar = ((1 << L) - r) % (1 << L)
        res_plus = reduce_T_plus(rbar, L)
        if res_plus is None:
            mismatches.append((r, rbar, "T+ rejected start"))
            continue
        pairs_checked += 1
        c_m, d_m, X_m, vK_m, vI_m = res_minus
        c_p, d_p, X_p, vK_p, vI_p = res_plus
        # Stepwise valuation match: lemma's central claim.
        if vK_m != vK_p or vI_m != vI_p:
            valuation_mismatches.append((r, rbar, vK_m, vK_p, vI_m, vI_p))
        # Terminal-data correspondence: c^+ = c^-, d^+ = -d^-.
        if c_p != c_m or d_p != -d_m:
            mismatches.append((r, rbar, "terminal (c, d) mismatch", (c_m, d_m), (c_p, d_p)))
        # X-criterion correspondence: X_m = 1 iff X_p = 1.
        if (X_m == 1) != (X_p == 1):
            mismatches.append((r, rbar, "X-criterion mismatch", X_m, X_p))
        if X_m == 1:
            minus_count += 1
            obstr_minus.add(r)
        if X_p == 1:
            plus_count += 1
            obstr_plus.add(rbar)

    print(f"Pairs (r, bar{{r}}) checked: {pairs_checked}")
    print(f"|Obstr_L^-| = {minus_count}")
    print(f"|Obstr_L^+| = {plus_count}  (counted via T+ reduction on the involution images)")
    print(f"Valuation-sequence mismatches: {len(valuation_mismatches)}")
    print(f"Terminal-data / X-criterion mismatches: {len(mismatches)}")

    # The bijection: r in Obstr_L^- iff (2^L - r) in Obstr_L^+.
    image_of_minus = {((1 << L) - r) % (1 << L) for r in obstr_minus}
    if image_of_minus == obstr_plus and not valuation_mismatches and not mismatches:
        print(
            f"\n✓ VERIFIED at L = {L}: the involution r -> 2^L - r is a bijection "
            f"Obstr_L^- <-> Obstr_L^+, valuation sequences agree step-by-step, "
            f"and terminal data satisfy (c^+, d^+) = (c^-, -d^-)."
        )
    else:
        print("\n✗ FAILED:")
        if valuation_mismatches:
            print(f"  {len(valuation_mismatches)} step-valuation mismatch(es); first 3: {valuation_mismatches[:3]}")
        if mismatches:
            print(f"  {len(mismatches)} terminal mismatch(es); first 3: {mismatches[:3]}")
        if image_of_minus != obstr_plus:
            sym_diff = image_of_minus.symmetric_difference(obstr_plus)
            print(f"  Bijection broken: |symmetric difference| = {len(sym_diff)}; sample: {sorted(sym_diff)[:5]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
