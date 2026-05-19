"""Computational verification of Theorem 5.2 (F1 construction).

Theorem 5.2: For each u ∈ {0,1}^n, the obstruction r_n = r_0 + sum_k u_k * 2^{6+k}
(with r_0 ∈ W_6 = {19, 27, 59}) is a obstruction in W_{6+n} with u as factor at position 6.

Verify computationally for all u ∈ {0,1}^n with n = 4, 6, 8.
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


def main():
    n_max = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    print(
        "Theorem 5.2 verification: construct r_n per Pattern u, verify r_n ∈ W_{6+n}\n"
    )

    W6 = [19, 27, 59]
    L0 = 6

    for n in range(1, n_max + 1):
        L = L0 + n
        print(f"n = {n}, L = {L}: ", end="")
        success_per_r0 = {r0: 0 for r0 in W6}
        total = 1 << n  # 2^n patterns

        for u_int in range(total):
            # Extract bits u_0, u_1, ..., u_{n-1}
            for r0 in W6:
                r_n = r0
                for k in range(n):
                    u_k = (u_int >> k) & 1
                    r_n += u_k * (1 << (L0 + k))
                # Verify r_n is obstruction at L
                if is_obstr(r_n, L):
                    # Verify u as factor at position 6
                    extracted = (r_n >> L0) & ((1 << n) - 1)
                    if extracted == u_int:
                        success_per_r0[r0] += 1
                    else:
                        print(
                            f"\n  Pattern extraction mismatch: u={u_int}, extracted={extracted}"
                        )

        # Overall stats
        any_r0_works = sum(
            1
            for u_int in range(total)
            if any(
                is_obstr(
                    r0 + sum(((u_int >> k) & 1) * (1 << (L0 + k)) for k in range(n)), L
                )
                for r0 in W6
            )
        )
        print(
            f"any-r0-obstructions = {any_r0_works}/{total} ({100*any_r0_works/total:.1f}%)"
        )
        for r0 in W6:
            print(
                f"  r0={r0:2d}: {success_per_r0[r0]:>4}/{total} ({100*success_per_r0[r0]/total:.1f}%)"
            )


if __name__ == "__main__":
    main()
