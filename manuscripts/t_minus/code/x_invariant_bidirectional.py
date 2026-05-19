"""Generalize T15-X-characterization to all r odd (any v_2(r-1)).

For r odd, m = (r-1)/2^v with v = v_2(r-1), the Iso trajectory starts at (m, 2^(L-v)).
Initial (c, d): a_I = (a_K - 1)/2^v, so c_0 = 1/2^v, d_0 = -1/2^v.
Initial X_0 = -2/2^v.

Conjecture: r is obstruction ⟺ X_end = 1 at max-uniform-reduction endpoint.
"""

from __future__ import annotations
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


def trace_X_general(r, L):
    if r % 2 == 0:
        return None
    v = v2(r - 1)
    if v == 0 or v >= L:
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
        a_K_new, b_K_new = step_K
        a_I_new, b_I_new = step_I
        v_K = v2(3 * a_K - 1)
        v_I = v2(3 * a_I - 1)
        c = c * Fraction(1 << v_K, 1 << v_I)
        d = (3 * d + c * Fraction(1 << v_I, 1 << v_K) - 1) / Fraction(1 << v_I)
        # Hmm, this update is wrong — need to use OLD c, not new c
        # Let me redo properly
        a_K, b_K = a_K_new, b_K_new
        a_I, b_I = a_I_new, b_I_new

    return {"a_K": a_K, "a_I": a_I, "c": c, "d": d, "X": 3 * d + c}


def trace_X_proper(r, L):
    """Properly compute (c, d, X) at endpoint via correct recursion."""
    if r % 2 == 0:
        return None
    v = v2(r - 1)
    if v == 0 or v >= L:
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
        # Compute v_K, v_I from current state BEFORE updating
        v_K_step = v2(3 * a_K - 1)
        v_I_step = v2(3 * a_I - 1)
        # Update c, d using OLD c
        c_old = c
        c = c_old * Fraction(1 << v_K_step, 1 << v_I_step)
        d = (3 * d + c_old - 1) / Fraction(1 << v_I_step)
        a_K, b_K = step_K
        a_I, b_I = step_I

    return {"a_K": a_K, "a_I": a_I, "c": c, "d": d, "X": 3 * d + c}


# Atomic obstructions
ATOMS = {
    6: {19, 27, 59},
    7: {79, 99},
    8: {67, 111, 157},
    9: {221, 303, 387, 447},
    10: {259, 431, 437, 551, 605, 831, 893},
}


def obstructions_mod(L):
    mod = 1 << L
    obstructions = set()
    for L_atom, atom_set in ATOMS.items():
        if L_atom > L:
            continue
        atom_mod = 1 << L_atom
        for a in atom_set:
            for j in range(0, mod, atom_mod):
                obstructions.add((a + j) % mod)
    return obstructions


def main():
    print("T15-X-characterization for ALL odd r (any v_2(r-1)):\n")

    for L in [6, 7, 8, 9]:
        mod = 1 << L
        obstructions = obstructions_mod(L)
        classes = [r for r in range(1, mod, 2) if v2(r - 1) >= 1 and v2(r - 1) < L]
        print(f"=== Mod 2^{L} = {mod} ===")
        print(f"  Total odd classes: {len(classes)}")
        print(f"  obstructions: {len([c for c in classes if c in obstructions])}")

        obstr_X1 = 0
        obstr_other = 0
        non_obstruction_X1 = 0
        non_obstruction_other = 0
        non_obstruction_X1_examples = []
        obstr_violations = []

        for r in classes:
            res = trace_X_proper(r, L)
            if res is None:
                continue
            x = res["X"]
            is_obstr = r in obstructions
            if x == 1:
                if is_obstr:
                    obstr_X1 += 1
                else:
                    non_obstruction_X1 += 1
                    non_obstruction_X1_examples.append(r)
            else:
                if is_obstr:
                    obstr_other += 1
                    obstr_violations.append((r, x))
                else:
                    non_obstruction_other += 1

        total_obstructions = obstr_X1 + obstr_other
        total_non_obstructions = non_obstruction_X1 + non_obstruction_other
        print(f"  obstructions with X=1: {obstr_X1}/{total_obstructions}")
        if obstr_violations:
            print(f"    Violations: {obstr_violations[:5]}")
        print(
            f"  Non-obstructions with X=1: {non_obstruction_X1}/{total_non_obstructions}"
        )
        if non_obstruction_X1_examples:
            print(f"    Examples: {non_obstruction_X1_examples[:5]}")
        print()


if __name__ == "__main__":
    main()
