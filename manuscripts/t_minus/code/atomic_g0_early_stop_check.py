"""Check whether parallel reduction at (r', L0-1) stops earlier than at (r, L0)
for G_0-obstructions r ∈ W_{L_0}^{G_0}.

For each G_0-obstruction r at level L_0:
  - Compute J_0 = number of reduction steps for (r, L_0) until stop.
  - Compute J' = number of reduction steps for (r', L_0-1) where r' = r mod 2^{L_0-1}.
  - Record (c, d) endpoint at (r', L_0-1).
  - Classify: (a) same number of steps J' = J_0 and endpoint (1, 0) -> G_0 anchor preserved
              (b) J' < J_0 and endpoint (4^a, (1-4^a)/3) for some a -> G_a anchor
              (c) J' < J_0 and endpoint is NOT shift-a normal form -> r' is NOT obstruction (problematic!)
              (d) J' > J_0 -> impossible (since reduction terminates monotonically)
"""

from __future__ import annotations
import sys
from fractions import Fraction
from collections import Counter


def v2(n):
    if n == 0:
        return 10**9  # treat as infinity
    n = abs(n)
    c = 0
    while (n & 1) == 0:
        n >>= 1
        c += 1
    return c


def parallel_reduce(r, L):
    """Run parallel T_- reduction for (r, L). Returns:
    (n_steps, (c, d) endpoint as Fraction, stop_type, V_K, V_I, V_K_final, V_I_final)
    stop_type: 'EE' or 'SS' or 'EARLY' (modular grace).
    """
    if r % 2 == 0:
        return None
    if r % 4 != 3:
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
    n_steps = 0
    while True:
        three_aK = 3 * a_K - 1
        v_K = v2(three_aK)
        v_b_K = v2(b_K)
        three_aI = 3 * a_I - 1
        v_I = v2(three_aI)
        v_b_I = v2(b_I)
        # Stop if either side can't advance.
        if v_K >= v_b_K or v_I >= v_b_I:
            # Stop type: EE iff v_K == v_b_K and v_I == v_b_I (both tight)
            #            SS iff v_K > v_b_K  and v_I > v_b_I (both strict)
            if v_K == v_b_K and v_I == v_b_I:
                stop_type = "EE"
            elif v_K > v_b_K and v_I > v_b_I:
                stop_type = "SS"
            else:
                stop_type = "MIXED"  # one tight, one strict
            return n_steps, (c, d), stop_type, V_K, V_I
        # Otherwise step both.
        c_old = c
        c = c_old * Fraction(1 << v_K, 1 << v_I)
        d = (3 * d + c_old - 1) / Fraction(1 << v_I)
        a_K = three_aK >> v_K
        b_K = (3 * b_K) >> v_K
        a_I = three_aI >> v_I
        b_I = (3 * b_I) >> v_I
        V_K += v_K
        V_I += v_I
        n_steps += 1


def is_obstr_endpoint(c, d):
    """Check if (c, d) is shift-a normal form: c = 4^a, d = (1-4^a)/3
    for a ∈ Z (allow negative a, where c = 1/4^|a|)."""
    # X = 3d + c
    X = 3 * d + c
    if X != 1:
        return None
    # Determine a from c. c must be a Fraction with c = 4^a:
    # either c = 4^a (a >= 0, c.denominator=1) or c = 1/4^|a| (a < 0, c.numerator=1).
    if c <= 0:
        return None
    # Test positive a
    if c.denominator == 1:
        c_int = c.numerator
        a = 0
        c_test = 1
        while c_test < c_int:
            c_test *= 4
            a += 1
        if c_test != c_int:
            return None
        expected_d = Fraction(1 - c_int, 3)
        if d != expected_d:
            return None
        return a
    # Test negative a (c = 1 / 4^|a|)
    if c.numerator == 1:
        denom = c.denominator
        a = 0
        d_test = 1
        while d_test < denom:
            d_test *= 4
            a += 1
        if d_test != denom:
            return None
        # c = 1 / 4^a, so "4^a" formally = 1/4^a; d expected = (1 - 1/4^a)/3
        expected_d = (1 - c) / 3
        if d != expected_d:
            return None
        return -a
    return None


def main():
    L = int(sys.argv[1]) if len(sys.argv) > 1 else 10

    # Find all G_0 obstructions at level L
    g0_obstructions = []
    for r in range(1, 1 << L, 2):
        result = parallel_reduce(r, L)
        if result is None:
            continue
        n_steps, (c, d), stop_type, V_K, V_I = result
        if 3 * d + c == 1:
            a = is_obstr_endpoint(c, d)
            if a == 0:
                g0_obstructions.append((r, n_steps, stop_type, V_K, V_I))

    print(f"L = {L}: {len(g0_obstructions)} G_0 obstructions found\n")

    # For each, check (r', L-1)
    classification = Counter()
    details = []
    for r, J0, stop_type, V_K_orig, V_I_orig in g0_obstructions:
        rp = r % (1 << (L - 1))
        result_p = parallel_reduce(rp, L - 1)
        if result_p is None:
            classification["rp_invalid"] += 1
            continue
        Jp, (cp, dp), stop_type_p, V_K_p, V_I_p = result_p
        ap = is_obstr_endpoint(cp, dp)
        if ap is None:
            classification["NOT_obstr_at_L-1"] += 1
            details.append((r, rp, J0, Jp, stop_type, stop_type_p, cp, dp, "NOT_obstr"))
        elif Jp == J0 and ap == 0:
            classification["same_steps_G0"] += 1
        elif Jp < J0:
            classification[f"early_stop_G{ap}"] += 1
            details.append((r, rp, J0, Jp, stop_type, stop_type_p, cp, dp, f"G{ap}"))
        elif Jp > J0:
            classification[f"later_stop_G{ap}"] += 1
            details.append(
                (r, rp, J0, Jp, stop_type, stop_type_p, cp, dp, f"G{ap}_later")
            )
        else:
            classification[f"same_steps_G{ap}"] += 1

    print("Classification of (r, L) G_0-obstructions wrt (r', L-1):")
    for k, v in sorted(classification.items()):
        print(f"  {k:30s}: {v}")

    if classification.get("NOT_obstr_at_L-1", 0) > 0:
        print(
            "\n*** Theorem 6.2 (no shift-zero atoms) VIOLATED: there exist "
            "G_0-obstructions r at L whose mod-2^{L-1} reduction is NOT an "
            "obstruction at L-1!"
        )
        print("Examples (r, rp, J0, Jp, stop_type, stop_type_p, c_p, d_p):")
        for d in details[:5]:
            if d[-1] == "NOT_obstr":
                print(f"  {d}")
    else:
        print(
            "\n*** Theorem 6.2 (no shift-zero atoms) holds empirically "
            "at L = {} ***".format(L)
        )

    if any("early_stop" in k for k in classification):
        print("\nNote: some G_0-obstructions have *early stop* at level L-1.")
        print("Example details (first 5):")
        early_count = 0
        for d in details:
            if "G" in d[-1] and "early" in str(d) or d[2] != d[3]:
                if d[-1] != "NOT_obstr":
                    print(
                        f"  r={d[0]}, rp={d[1]}, J0={d[2]}, Jp={d[3]}, "
                        f"stop_type@L={d[4]}, stop_type@L-1={d[5]}, "
                        f"endpoint@L-1: c={d[6]} d={d[7]} -> {d[-1]}"
                    )
                    early_count += 1
                    if early_count >= 5:
                        break


if __name__ == "__main__":
    main()
