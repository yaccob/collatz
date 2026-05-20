"""Empirical test of Quasi-Uniformity Lemma for obstruction language.

Claim: For each fixed u ∈ {0,1}^n and position j, the fraction
  |{r ∈ W_L : w_r[j..j+n-1] = u}| / |W_L|
converges to 1/2^n as L → ∞.

If this holds, Conjecture F1 (p_W(n) = 2^n) follows trivially: each pattern
u has positive density of obstructions containing it as factor at every position,
so coverage → ∞ as L → ∞.

Strategy:
1. Collect W_L via X_end characterization.
2. For each n (test n ∈ {4, 6, 8, 10}):
   For each j ∈ {0, ..., L-n}:
     For each u ∈ {0,1}^n: count obstructions with w_r[j..j+n-1] = u
   Compute mean / variance / max deviation from uniform.
3. As L grows: deviation should shrink if uniformity holds.
"""

from __future__ import annotations
import math
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
    three_a_minus_1 = 3 * a - 1
    v_a = v2(three_a_minus_1)
    v_b = v2(b) if b != 0 else 99
    if v_a >= v_b:
        return None
    return (three_a_minus_1 // (1 << v_a), (3 * b) // (1 << v_a))


def x_end(r, L):
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
    return 3 * d + c


def obstructions_at(L):
    return [r for r in range(1, 1 << L, 2) if (x := x_end(r, L)) is not None and x == 1]


def factor_distribution(obstructions, L, n, j):
    """Return dict {u: count} of obstructions with w_r[j..j+n-1] == u."""
    mask = (1 << n) - 1
    counts = {}
    for r in obstructions:
        u = (r >> j) & mask
        counts[u] = counts.get(u, 0) + 1
    return counts


def uniformity_metrics(counts, n, total):
    expected = total / (1 << n)
    if expected == 0:
        return None
    values = list(counts.values())
    # Fill in 0-counts for patterns not seen
    while len(values) < (1 << n):
        values.append(0)
    values = values + [0] * ((1 << n) - len(values))
    values = values[: 1 << n]
    # Actually: rebuild for full coverage
    full = [counts.get(u, 0) for u in range(1 << n)]
    mean = sum(full) / len(full)
    var = sum((v - mean) ** 2 for v in full) / len(full)
    max_dev = max(abs(v - expected) for v in full)
    min_count = min(full)
    max_count = max(full)
    return {
        "expected": expected,
        "mean": mean,
        "var": var,
        "sd": math.sqrt(var),
        "max_dev": max_dev,
        "min_count": min_count,
        "max_count": max_count,
        "missing": sum(1 for v in full if v == 0),
    }


def main():
    L_max = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    print(f"Quasi-uniformity test, L = 6..{L_max}\n")

    for L in range(8, L_max + 1):
        obstructions = obstructions_at(L)
        n_obstructions = len(obstructions)
        print(f"L = {L:2d}: |W_L| = {n_obstructions}", flush=True)

        # Test patterns of length n at position j (middle to avoid bit-0 oddness)
        for n in [4, 6, 8]:
            if n >= L:
                continue
            j = (L - n) // 2  # middle position
            counts = factor_distribution(obstructions, L, n, j)
            m = uniformity_metrics(counts, n, n_obstructions)
            if m is None:
                continue
            patterns_seen = len(counts)
            expected = n_obstructions / (1 << n)
            print(
                f"  n={n}, j={j:>2}: patterns_seen={patterns_seen}/{1<<n}, "
                f"E[count]={expected:>6.2f}, mean={m['mean']:>6.2f}, "
                f"sd={m['sd']:>6.2f}, sd/E={m['sd']/expected:.3f}, "
                f"max_dev={m['max_dev']:>5.1f}, missing={m['missing']}",
                flush=True,
            )

    # Asymptotic test: how does sd/expected scale with L for fixed n?
    print("\nAsymptotic scaling (n=6, j=middle):", flush=True)
    print("  L | |W_L| | E[count] |   sd   | sd/E  | missing", flush=True)
    print(" ---|-------|----------|--------|-------|--------", flush=True)
    for L in range(10, L_max + 1):
        obstructions = obstructions_at(L)
        n = 6
        j = (L - n) // 2
        counts = factor_distribution(obstructions, L, n, j)
        m = uniformity_metrics(counts, n, len(obstructions))
        if m is None:
            continue
        expected = len(obstructions) / (1 << n)
        print(
            f" {L:>2} | {len(obstructions):>5} | {expected:>8.2f} | {m['sd']:>6.2f} | "
            f"{m['sd']/expected:.3f} | {m['missing']:>3}",
            flush=True,
        )

    print(
        "\n  Note: auxiliary pattern-distribution statistics; "
        "no rigorous claim attached. Quasi-uniformity (sd/E → 0 as L grows) "
        "is a heuristic, not a theorem in the manuscript.",
        flush=True,
    )


if __name__ == "__main__":
    main()
