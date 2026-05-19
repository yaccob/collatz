"""Factor complexity p_W(n) of the obstruction language L_W.

For each L = L_min..L_max:
  1. Enumerate obstruction classes W_L = {r odd : X_end(r) = 1} mod 2^L.
  2. Represent each r as L-bit word (LSB-first AND MSB-first separately).
  3. Collect distinct n-factors p_n^L = {u : u factor of some w_r, |u| = n}.
  4. p_W(n) := union over L >= n of p_n^L (stabilizes at L = n + const).

Compare growth rate vs. phi^n (golden ratio), beta^n (tribonacci ~1.839),
2^n, and polynomial.

Discriminates:
  - p_W(n) = Theta(phi^n): obstruction language is sofic with entropy log_2 phi
            => candidate for beta-shift / sofic shift class
  - p_W(n) = 2^n - o(2^n): no sub-exponential structure
  - p_W(n) polynomial: very restricted (Sturmian-like, but already falsified)
"""

from __future__ import annotations
import math
import sys
from fractions import Fraction


def v2(n: int) -> int:
    if n == 0:
        return -1
    n = abs(n)
    c = 0
    while (n & 1) == 0:
        n >>= 1
        c += 1
    return c


def step_T_minus(a: int, b: int):
    three_a_minus_1 = 3 * a - 1
    v_a = v2(three_a_minus_1)
    v_b = v2(b) if b != 0 else 99
    if v_a >= v_b:
        return None
    return (three_a_minus_1 // (1 << v_a), (3 * b) // (1 << v_a))


def x_end(r: int, L: int):
    """Return X_end as Fraction, or None if reduction can't start."""
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


def obstructions_at(L: int) -> list[int]:
    """Return sorted list of obstruction classes r in [1, 2^L) odd with X_end(r) = 1."""
    out = []
    for r in range(1, 1 << L, 2):
        x = x_end(r, L)
        if x is not None and x == 1:
            out.append(r)
    return out


def bits_lsb(r: int, L: int) -> str:
    return "".join(str((r >> j) & 1) for j in range(L))


def bits_msb(r: int, L: int) -> str:
    return format(r, f"0{L}b")


def factors_of(word: str, n: int) -> set[str]:
    return (
        {word[i : i + n] for i in range(len(word) - n + 1)} if n <= len(word) else set()
    )


def factor_complexity_from_words(words: list[str], n: int) -> set[str]:
    all_facs: set[str] = set()
    for w in words:
        all_facs |= factors_of(w, n)
    return all_facs


def main():
    L_max = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    print(f"obstruction-language factor complexity, L = 6..{L_max}\n")

    # Step 1: enumerate obstructions per L
    obstructions_per_L: dict[int, list[int]] = {}
    for L in range(6, L_max + 1):
        obstructions_per_L[L] = obstructions_at(L)
        print(f"L={L:2d}: |W_L| = {len(obstructions_per_L[L]):>5d}")
    print()

    # Step 2: build LSB / MSB obstruction-word sets
    words_lsb_per_L = {
        L: [bits_lsb(r, L) for r in obstructions_per_L[L]] for L in obstructions_per_L
    }
    words_msb_per_L = {
        L: [bits_msb(r, L) for r in obstructions_per_L[L]] for L in obstructions_per_L
    }

    # Step 3: factor complexity p_W(n) over the LARGEST L (which dominates)
    L_use = L_max
    print(f"Factor complexity computed from L={L_use} obstruction-words (LSB-first):\n")
    print("  n |   p_W(n) |     2^n |  phi^n  | beta^n  | p_W/phi^n | p_W/beta^n")
    print(" ---|---------:|--------:|--------:|--------:|----------:|----------:")
    phi = (1 + math.sqrt(5)) / 2
    beta = 1.83928675521416  # tribonacci constant
    p_W_lsb = {}
    p_W_msb = {}
    for n in range(1, L_use):
        facs_lsb = factor_complexity_from_words(words_lsb_per_L[L_use], n)
        facs_msb = factor_complexity_from_words(words_msb_per_L[L_use], n)
        p_W_lsb[n] = len(facs_lsb)
        p_W_msb[n] = len(facs_msb)

    for n in range(1, L_use):
        p = p_W_lsb[n]
        print(
            f" {n:2d} | {p:>8d} | {2**n:>7d} | {phi**n:>7.2f} | {beta**n:>7.2f} | "
            f"{p / phi**n:>9.3f} | {p / beta**n:>9.3f}"
        )

    print()
    print(f"Factor complexity (MSB-first), L={L_use}:\n")
    print("  n |   p_W(n) |  p_W/phi^n | p_W/beta^n")
    print(" ---|---------:|----------:|----------:")
    for n in range(1, L_use):
        p = p_W_msb[n]
        print(f" {n:2d} | {p:>8d} | {p / phi**n:>9.3f} | {p / beta**n:>9.3f}")

    print()
    # Step 4: stability check — does p_W(n) saturate as L grows?
    print("Stability of p_W(n) across L (LSB-first):\n")
    L_test = [L for L in obstructions_per_L if L >= 8]
    n_show = min(8, L_max - 1)
    header = "  n | " + " | ".join(f"L={L}" for L in L_test)
    print(header)
    print(" ---|" + "---|" * len(L_test))
    for n in range(1, n_show + 1):
        row = f" {n:2d} | "
        vals = []
        for L in L_test:
            facs = factor_complexity_from_words(words_lsb_per_L[L], n)
            vals.append(f"{len(facs):>3d}")
        row += " | ".join(vals)
        print(row)

    # Step 5: log-fit growth rate
    print()
    print(f"Growth rate fit (log p_W(n) vs n, LSB-first, L={L_use}):\n")
    ns_fit = list(range(3, min(10, L_use)))
    if len(ns_fit) >= 2:
        log_p = [math.log(p_W_lsb[n]) for n in ns_fit]
        # linear fit
        mean_n = sum(ns_fit) / len(ns_fit)
        mean_lp = sum(log_p) / len(log_p)
        num = sum((n - mean_n) * (lp - mean_lp) for n, lp in zip(ns_fit, log_p))
        den = sum((n - mean_n) ** 2 for n in ns_fit)
        slope = num / den if den != 0 else 0
        intercept = mean_lp - slope * mean_n
        print(f"  log p_W(n) ≈ {slope:.4f} * n + {intercept:.4f}")
        print(f"  => p_W(n) ≈ {math.exp(intercept):.3f} * {math.exp(slope):.4f}^n")
        print(f"  Compare:  phi = {phi:.4f}  beta = {beta:.4f}  2 = 2.0000")
        # Theorem 1.3 / 5.1 predicts p_W(n) = 2^n once L is large enough that the
        # construction at level 6 + n fits inside the enumeration window.
        if abs(slope - math.log(2)) < 0.01:
            print("\n✓ VERIFIED: empirical slope matches log 2 within 0.01 (Theorem 1.3 / 5.1).")
        else:
            print(f"\n✗ FAILED: empirical slope {slope:.4f} deviates from log 2 = {math.log(2):.4f}.")


if __name__ == "__main__":
    main()
