"""Empirical verification of the atom decomposition (`lem:atom-decomp`):
every obstruction r ∈ Ω_L has a unique atomic anchor r_0 ∈ A_{L_0} (L_0 ≤ L)
and bit-choice u such that r = r_0 + Σ u_k · 2^{L_0 + k}.

For each r ∈ Ω_L: find the smallest L_0 such that r mod 2^{L_0} ∈ Ω_{L_0}
but r mod 2^{L_0 - 1} ∉ Ω_{L_0 - 1} (i.e. atomic at L_0).
"""

from __future__ import annotations
import sys
from fractions import Fraction
from collections import Counter


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
    three_a_minus_1 = 3 * a - 1
    v_a = v2(three_a_minus_1)
    v_b = v2(b) if b != 0 else 99
    if v_a >= v_b:
        return None
    return (three_a_minus_1 // (1 << v_a), (3 * b) // (1 << v_a))


def is_obstr(r, L):
    if r % 2 == 0:
        return False
    v = v2(r - 1)
    if v <= 0 or v >= L:
        return False
    factor = 1 << v
    m = (r - 1) // factor
    a_K, b_K = r, 1 << L
    a_I, b_I = m, 1 << (L - v)
    c = Fraction(1, factor)
    d = Fraction(-1, factor)
    while True:
        step_K = step_T_minus(a_K, b_K)
        step_I = step_T_minus(a_I, b_I)
        if step_K is None or step_I is None:
            break
        v_K_step = v2(3 * a_K - 1)
        v_I_step = v2(3 * a_I - 1)
        c_old = c
        c = c_old * Fraction(1 << v_K_step, 1 << v_I_step)
        d = (3 * d + c_old - 1) / Fraction(1 << v_I_step)
        a_K, b_K = step_K
        a_I, b_I = step_I
    return 3 * d + c == 1


def find_atomic_L0(r, L):
    """Find smallest L_0 ≤ L such that r mod 2^{L_0} is obstruction at L_0
    AND r mod 2^{L_0-1} is not obstruction at L_0-1. Returns L_0."""
    for L0 in range(5, L + 1):
        r_mod = r % (1 << L0)
        if is_obstr(r_mod, L0):
            if not is_obstr(r % (1 << (L0 - 1)), L0 - 1):
                return L0, r_mod
    return None, None


def main():
    L = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    print(f"Atomic anchor verification at L = {L}\n")

    obstructions = [r for r in range(1, 1 << L, 2) if is_obstr(r, L)]
    print(f"|W_L| = {len(obstructions)}")

    atomic_counts = Counter()
    atomic_obstructions = {}  # L_0 → list of r_0 values

    for r in obstructions:
        L0, r0 = find_atomic_L0(r, L)
        if L0 is None:
            print(f"  WARN: r={r} has no atomic anchor")
            continue
        atomic_counts[L0] += 1
        atomic_obstructions.setdefault(L0, set()).add(r0)

    print("\nAnchor distribution per L_0:")
    print(
        "  L_0 | obstructions anchored | |A_{L_0}| (distinct r_0) | predicted = |A_{L_0}| · 2^{L-L_0}"
    )
    expected_sum = 0
    for L0 in sorted(atomic_counts.keys()):
        actual = atomic_counts[L0]
        n_r0 = len(atomic_obstructions[L0])
        predicted = n_r0 * (1 << (L - L0))
        expected_sum += predicted
        match = "✓" if actual == predicted else "✗"
        print(f"  {L0:>3} | {actual:>14} | {n_r0:>20} | {predicted:>5} {match}")
    print(f"\nTotal: {expected_sum} (= |W_L| = {len(obstructions)})")
    ok = expected_sum == len(obstructions)
    print(
        f"Identity |Ω_L| = Σ |A_{{L_0}}| · 2^{{L-L_0}}: {'✓ VERIFIED' if ok else '✗ FAILED'}"
    )
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
