"""Test whether X = 1 at endpoint applies to NON-OBSTRUCTION classes as well.

If yes: the obstruction property is orthogonal to Lemma G — Lemma G holds for
all classes, and obstructions are characterized by additional dynamics.

If no: the obstruction property is what enforces X = 1 — and we must understand
the connection.
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
        return None, v_a, v_b
    return (three_a_minus_1 // (1 << v_a), (3 * b) // (1 << v_a)), v_a, v_b


def trace_X(r, L):
    """Return list of (c, d, X, E) along max-uniform reduction."""
    if r % 4 != 3 or v2(r - 1) != 1:
        return None
    m = (r - 1) // 2
    a_K, b_K = r, 1 << L
    a_I, b_I = m, 1 << (L - 1)
    c = Fraction(1, 2)
    d = Fraction(-1, 2)

    trace = []
    while True:
        E = 3 * a_I - 1 - c * (3 * a_K - 1)
        X = 3 * d + c
        trace.append(
            {"j": len(trace), "a_K": a_K, "a_I": a_I, "c": c, "d": d, "X": X, "E": E}
        )
        step_K, v_K, _ = step_T_minus(a_K, b_K)
        step_I, v_I, _ = step_T_minus(a_I, b_I)
        if step_K is None or step_I is None:
            break
        c_new = c * Fraction(1 << v_K, 1 << v_I)
        d_new = (3 * d + c - 1) / Fraction(1 << v_I)
        c = c_new
        d = d_new
        a_K, b_K = step_K
        a_I, b_I = step_I

    return trace


def classify_obstr_at_level(L):
    """obstructions in t_{-1} ∩ t_{-3} mod 2^L (rigorously known)."""
    # Atomic rigorous obstructions per level
    atoms = {
        6: {19, 27, 59},
        7: {79, 99},
        8: {67, 111, 157},
        9: {221, 303, 387, 447},
        10: {259, 431, 437, 551, 605, 831, 893},
    }
    mod = 1 << L
    obstructions = set()
    for L_atom, atom_set in atoms.items():
        if L_atom > L:
            continue
        atom_mod = 1 << L_atom
        for a in atom_set:
            for j in range(0, mod, atom_mod):
                obstructions.add((a + j) % mod)
    classes = [r for r in range(3, mod, 4) if v2(r - 1) == 1]
    return classes, obstructions


def classify_obstr_mod64():
    return classify_obstr_at_level(6)


def main():
    print("Test: X = 1 at endpoint CHARACTERIZES obstructions?\n")

    for L in [6, 7, 8, 9]:
        classes, obstructions = classify_obstr_at_level(L)
        print(f"=== Mod 2^{L} = {1<<L} ===")
        print(f"  Classes (r ≡ 3 mod 4, v_2(r-1)=1): {len(classes)}")
        print(
            f"  obstructions (rigorous): {len(classes & obstructions) if isinstance(classes, set) else len([c for c in classes if c in obstructions])}"
        )

        obstr_X1_count = 0
        obstr_other = 0
        non_obstruction_X1_count = 0
        non_obstruction_other = 0
        obstr_violations = []
        non_obstruction_X1_examples = []

        for r in classes:
            trace = trace_X(r, L)
            if trace is None:
                continue
            X_end = trace[-1]["X"]
            is_obstr = r in obstructions
            X_is_1 = X_end == 1
            if is_obstr and X_is_1:
                obstr_X1_count += 1
            elif is_obstr and not X_is_1:
                obstr_other += 1
                obstr_violations.append((r, X_end))
            elif (not is_obstr) and X_is_1:
                non_obstruction_X1_count += 1
                non_obstruction_X1_examples.append(r)
            else:
                non_obstruction_other += 1

        total_obstructions = obstr_X1_count + obstr_other
        total_non_obstructions = non_obstruction_X1_count + non_obstruction_other
        print(f"  obstructions with X=1: {obstr_X1_count}/{total_obstructions}")
        if obstr_violations:
            print(f"    obstruction violations: {obstr_violations}")
        print(
            f"  Non-obstructions with X=1: {non_obstruction_X1_count}/{total_non_obstructions}"
        )
        if non_obstruction_X1_examples:
            print(
                f"    Non-obstruction X=1 examples: {non_obstruction_X1_examples[:5]}"
            )
        print()


if __name__ == "__main__":
    main()
