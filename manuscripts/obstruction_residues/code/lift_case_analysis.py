"""Detailed case analysis for Lift-Lemma.

For each obstruction r_0 ∈ W_{L_0}: classify
  - Lemma G_a class (a value)
  - Stop type: equality (v_K = v_b) or strict (v_K > v_b) at endpoint
  - Lift outcome: does r_+ and r_- lift, with what new G_b class?

Goal: identify all (a, stop_type) configurations and verify that lift always works,
via rigorous arguments per case.
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


def trace_full(r, L):
    """Returns dict with full trace info: a_K_end, a_I_end, V_K, V_I, c, d, X, stop_v_K, stop_v_bK."""
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
    V_K = 0
    V_I = 0
    while True:
        step_K = step_T_minus(a_K, b_K)
        step_I = step_T_minus(a_I, b_I)
        if step_K is None or step_I is None:
            # Record stop info
            stop_v_K = v2(3 * a_K - 1)
            stop_v_bK = v2(b_K)
            stop_v_I = v2(3 * a_I - 1)
            stop_v_bI = v2(b_I)
            break
        v_K_step = v2(3 * a_K - 1)
        v_I_step = v2(3 * a_I - 1)
        c_old = c
        c = c_old * Fraction(1 << v_K_step, 1 << v_I_step)
        d = (3 * d + c_old - 1) / Fraction(1 << v_I_step)
        a_K, b_K = step_K
        a_I, b_I = step_I
        V_K += v_K_step
        V_I += v_I_step
    return {
        "v": v,
        "a_K_end": a_K,
        "a_I_end": a_I,
        "b_K_end": b_K,
        "b_I_end": b_I,
        "c": c,
        "d": d,
        "X": 3 * d + c,
        "V_K": V_K,
        "V_I": V_I,
        "stop_v_K": stop_v_K,
        "stop_v_bK": stop_v_bK,
        "stop_v_I": stop_v_I,
        "stop_v_bI": stop_v_bI,
    }


def identify_G(c, d, X):
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
    L0 = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    print(f"Lift-Lemma case analysis at L_0 = {L0}\n")

    cases = defaultdict(int)
    detailed = defaultdict(list)
    for r in range(1, 1 << L0, 2):
        res = trace_full(r, L0)
        if res is None or res["X"] != 1:
            continue
        a = identify_G(res["c"], res["d"], res["X"])
        # Stop type
        stop_K_equal = res["stop_v_K"] == res["stop_v_bK"]
        stop_I_equal = res["stop_v_I"] == res["stop_v_bI"]
        # Stop trigger
        K_stops = res["stop_v_K"] >= res["stop_v_bK"]
        I_stops = res["stop_v_I"] >= res["stop_v_bI"]
        if K_stops and I_stops:
            trigger = "both"
            stop_type = (
                "EE"
                if stop_K_equal and stop_I_equal
                else "ES" if stop_K_equal else "SE" if stop_I_equal else "SS"
            )
        elif K_stops:
            trigger = "K"
            stop_type = "K_eq" if stop_K_equal else "K_strict"
        else:
            trigger = "I"
            stop_type = "I_eq" if stop_I_equal else "I_strict"

        key = (a, trigger, stop_type)
        cases[key] += 1
        detailed[key].append(r)

    print("Case distribution (a, trigger, type):")
    print("  a | trigger | stop_type | count | examples")
    for key in sorted(cases.keys(), key=lambda k: (k[0] is None, k[0], k[1], k[2])):
        a, trigger, stop_type = key
        cnt = cases[key]
        ex = detailed[key][:3]
        print(f"  {a:>3} | {trigger:>7} | {stop_type:>9} | {cnt:>5} | {ex}")

    print(
        "\n  Note: auxiliary case-distribution; no rigorous claim attached. "
        "Cross-references the EE/SS classification in §3 of the manuscript."
    )


if __name__ == "__main__":
    main()
