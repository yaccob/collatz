"""Test Lift-Lemma for obstructions of Lemma G_a class at L_0 -> L_0 + 1.

Lift-Lemma claim: For each obstruction r_0 ∈ W_{L_0}, both sub-classes
r_+ = r_0 (bit at position L_0 is 0) and r_- = r_0 + 2^{L_0} (bit at position
L_0 is 1) are obstructions in W_{L_0 + 1}.

If Lift-Lemma holds for ALL obstructions: |W_{L+1}| ≥ 2 |W_L|, hence |W_L|/2^L is
monotone non-decreasing, hence K6' rigorous with c_W ≥ |W_{L_0}|/2^{L_0}.

This script:
1. For each obstruction r_0 ∈ W_{L_0}: identify Lemma G_a class.
2. For each L_0 ∈ {6, 8, 10, 12}: check both r_+ and r_- at L_0 + 1.
3. Tabulate which Lemma G_a → Lemma G_? at L_0 + 1.
"""

from __future__ import annotations
import sys
from fractions import Fraction
from collections import defaultdict
from math import log2


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


def trace_X(r, L):
    """Return (X, c, d, a_end) at endpoint."""
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
    return (3 * d + c, c, d, a_K)


def identify_G_a(c, d, X):
    """Return Lemma G_a index, or None if not a obstruction endpoint."""
    if X != 1:
        return None
    if c <= 0:
        return None
    try:
        log_c = log2(float(c))
        if log_c.is_integer() and int(log_c) % 2 == 0:
            return int(log_c) // 2
    except (ValueError, OverflowError):
        pass
    return None


def main():
    L_list = [int(x) for x in (sys.argv[1:] or ["5", "6", "7", "8", "9", "10", "11", "12"])]
    print(f"Lift theorem test (Theorems 3.1/3.2 of the manuscript), L_0 ∈ {L_list}\n")

    any_failure = [False]

    for L0 in L_list:
        obstructions_L0 = []
        for r in range(1, 1 << L0, 2):
            res = trace_X(r, L0)
            if res is None:
                continue
            X, c, d, _ = res
            if X != 1:
                continue
            a = identify_G_a(c, d, X)
            obstructions_L0.append((r, a))

        print(f"L_0 = {L0}: {len(obstructions_L0)} obstructions")

        # Test Lift-Lemma: for each r_0 ∈ W_{L_0}, are both r_+ and r_- in W_{L_0+1}?
        lift_table = defaultdict(
            lambda: [0, 0, 0]
        )  # (a_at_L0): [count, lift_+, lift_-]
        for r0, a0 in obstructions_L0:
            # r_+ = r0 at L = L0 + 1
            r_plus = r0
            r_minus = r0 + (1 << L0)
            res_plus = trace_X(r_plus, L0 + 1)
            res_minus = trace_X(r_minus, L0 + 1)
            X_plus = res_plus[0] if res_plus else None
            X_minus = res_minus[0] if res_minus else None
            lift_table[a0][0] += 1
            if X_plus == 1:
                lift_table[a0][1] += 1
            if X_minus == 1:
                lift_table[a0][2] += 1

        for a in sorted(lift_table.keys(), key=lambda x: (x is None, x)):
            cnt, lp, lm = lift_table[a]
            print(
                f"  Lemma G_{a}: {cnt} obstructions, r_+ lifted: {lp}/{cnt}, "
                f"r_- lifted: {lm}/{cnt}, total at L+1: {lp + lm}/{2 * cnt}"
            )

        # Summary
        total = sum(t[0] for t in lift_table.values())
        total_lp = sum(t[1] for t in lift_table.values())
        total_lm = sum(t[2] for t in lift_table.values())
        print(
            f"  TOTAL: {total} obstructions, {total_lp + total_lm}/{2 * total} sub-classes lifted "
            f"({100 * (total_lp + total_lm) / (2 * total):.1f}%)"
        )
        if total_lp + total_lm != 2 * total:
            any_failure[0] = True
        print()

    if any_failure[0]:
        print("✗ FAILED: some obstruction did not lift to both r_+ and r_- at level L_0+1.")
        sys.exit(1)
    else:
        print(f"✓ VERIFIED: every obstruction at every tested L_0 lifts to both r_+ and r_-.")


if __name__ == "__main__":
    main()
