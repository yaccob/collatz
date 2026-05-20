"""Verify prediction from Theorems 3.1 + 3.2 / Proposition 3.3 case analysis:

  Stop type at r_+, L_0  |  r_+, L_0+1 endpoint  |  r_-, L_0+1 endpoint
  ----------------------|----------------------|----------------------
  EE (equality)         |  Lemma G_0 (extra)   |  Lemma G_a (same)
  SS (strict)           |  Lemma G_a (same)    |  Lemma G_0 (extra)

Compute the actual endpoint Lemma-G_b for r_+ and r_- at L_0+1, verify pattern.
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


def trace_endpoint(r, L):
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
            stop_v_K = v2(3 * a_K - 1)
            stop_v_bK = v2(b_K)
            break
        v_K_step = v2(3 * a_K - 1)
        v_I_step = v2(3 * a_I - 1)
        c_old = c
        c = c_old * Fraction(1 << v_K_step, 1 << v_I_step)
        d = (3 * d + c_old - 1) / Fraction(1 << v_I_step)
        a_K, b_K = step_K
        a_I, b_I = step_I
    return c, d, 3 * d + c, stop_v_K, stop_v_bK


def identify_G(c, d, X):
    if X != 1 or c <= 0:
        return None
    try:
        log_c = log2(float(c))
        if log_c.is_integer() and int(log_c) % 2 == 0:
            return int(log_c) // 2
    except (ValueError, OverflowError):
        pass
    return None


def main():
    L0 = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    print(f"Symmetry verification at L_0 = {L0}\n")
    print("Prediction:")
    print("  r_+ EE / r_- SS → Lemma G_0 (extra step)")
    print("  r_+ SS / r_- EE → Lemma G_a (same a)")
    print()

    table = defaultdict(int)  # (a, stop_type, who, b_observed) → count
    for r0 in range(1, 1 << L0, 2):
        res0 = trace_endpoint(r0, L0)
        if res0 is None:
            continue
        c0, d0, X0, vK_stop, vb_stop = res0
        if X0 != 1:
            continue
        a0 = identify_G(c0, d0, X0)
        stop_type = "EE" if vK_stop == vb_stop else "SS"
        # r_+ at L0+1
        res_p = trace_endpoint(r0, L0 + 1)
        b_p = identify_G(*res_p[:3]) if res_p and res_p[2] == 1 else "no-obstruction"
        # r_- at L0+1
        rminus = r0 + (1 << L0)
        res_m = trace_endpoint(rminus, L0 + 1)
        b_m = identify_G(*res_m[:3]) if res_m and res_m[2] == 1 else "no-obstruction"
        table[(a0, stop_type, "r+", b_p)] += 1
        table[(a0, stop_type, "r-", b_m)] += 1

    # Print observation table
    print("Observed lift behavior (a₀, stop_type, who, b_observed) → count:")
    mismatches = 0
    for key in sorted(
        table.keys(), key=lambda k: (k[0] is None, k[0], k[1], k[2], str(k[3]))
    ):
        a0, stop_type, who, b = key
        cnt = table[key]
        # Predicted b
        if stop_type == "EE":
            if who == "r+":
                predicted = 0
            else:
                predicted = a0  # r_- stays Lemma G_a
        else:  # SS
            if who == "r+":
                predicted = a0  # r_+ stays
            else:
                predicted = 0  # r_- → G_0
        match = "✓" if b == predicted else "✗ predicted G_" + str(predicted)
        print(f"  G_{a0} {stop_type} {who}: → G_{b}  (count={cnt:>4})  {match}")
        if b != predicted:
            mismatches += 1

    if mismatches == 0:
        print("\n✓ VERIFIED: §3.3 symmetry table holds at every (a, stop_type, lift) row.")
    else:
        print(f"\n✗ FAILED: {mismatches} rows deviate from the predicted §3.3 symmetry.")
        sys.exit(1)


if __name__ == "__main__":
    main()
