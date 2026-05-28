"""Independent re-enumeration of |Obs_L|, by a deliberately different algorithm.

This is a cross-check oracle for count_obstructions.py (and its Rust mirror).
Both of those track the affine pair (c, d) of Lemma lem:affine step by step via
the recursion d_{j+1} = (3 d_j + c_j - 1) / 2^{v_I}, and test 3 d_J + c_J = 1.
A systematic error in that shared recursion would be invisible to a Python-vs-
Rust comparison, since the Rust code is a line-by-line port of the Python one.

To get genuine *algorithmic* independence this module never forms the (c, d)
recursion at all:

  * It iterates the two tracks as the plain T_- trajectories of r and of
    m = (r-1)/2^v, exactly as Definition def:obstruction prescribes
    (a_K^(j) = T_-^j(r), a_I^(j) = T_-^j(m)).
  * At the common termination index J it reconstructs the X-invariant directly
    from the concrete terminal states, using only the cumulative valuations:
        c_J = 2^delta,  delta = V_K - V_I - v,
        d_J = a_I^(J) - c_J a_K^(J),
        X   = 3 d_J + c_J = 3 a_I^(J) - c_J (3 a_K^(J) - 1).
  * It stays in pure integer arithmetic (no Fraction, no dyadic struct): for
    delta < 0 the test X = 1 is cleared of denominators by multiplying through
    by 2^{-delta}.

So the only thing shared with the canonical implementations is the manuscript
definition itself (which T_- step fires, when the modulus is exhausted), not
the bookkeeping that turns it into an obstruction certificate.
"""
import sys


def v2(n):
    """2-adic valuation of a nonzero integer."""
    return (n & -n).bit_length() - 1


def is_obstruction(r, L):
    """Decide r in Obs_L by running the two T_- trajectories to their common
    stop and reconstructing X_end = 3 d_J + c_J from the terminal states."""
    if r & 1 == 0 or r == 1:
        return False
    v = v2(r - 1)
    if not (1 <= v < L):
        return False

    a_K = r
    a_I = (r - 1) >> v          # m = (r-1)/2^v
    V_K = 0                     # cumulative valuation on the K-track, = V_K^(j)
    V_I = 0                     # cumulative valuation on the I-track, = V_I^(j)

    while True:
        v_K = v2(3 * a_K - 1)
        v_I = v2(3 * a_I - 1)
        # Residual 2-adic capacity of each modulus (Section sec:setup):
        avail_K = L - V_K
        avail_I = (L - v) - V_I
        if v_K >= avail_K or v_I >= avail_I:
            # Common termination index J reached. Reconstruct X_end directly.
            delta = V_K - V_I - v
            if delta >= 0:
                # X = 3 a_I - 2^delta (3 a_K - 1); obstruction iff X == 1.
                return 3 * a_I - (1 << delta) * (3 * a_K - 1) == 1
            # delta < 0: clear the 2^delta denominator by * 2^{-delta}.
            e = -delta
            return 3 * (1 << e) * a_I - (3 * a_K - 1) == (1 << e)
        a_K = (3 * a_K - 1) >> v_K
        a_I = (3 * a_I - 1) >> v_I
        V_K += v_K
        V_I += v_I


def obstructions(L):
    """Sorted list of all obstruction residues in {1, ..., 2^L}."""
    return [r for r in range(1, 1 << L, 2) if is_obstruction(r, L)]


# Counts published in Table tab:appendix-counts of obstruction_residues.tex.
MANUSCRIPT_COUNTS = {
    5: 1, 6: 3, 7: 8, 8: 19, 9: 42, 10: 91,
    11: 194, 12: 409, 13: 855, 14: 1776, 15: 3671, 16: 7556,
}


def main():
    args = sys.argv[1:]
    cross_check = "--cross-check" in args
    positional = [a for a in args if not a.startswith("--")]

    if positional:
        L_lo = L_hi = int(positional[0])
        if len(positional) > 1:
            L_hi = int(positional[1])
    else:
        L_lo, L_hi = 5, 16

    canonical = None
    if cross_check:
        import count_obstructions  # local import: only needed for --cross-check

    print(f"# independent re-enumeration of |Obs_L|, L = {L_lo}..{L_hi}")
    print(f"# {'L':>3} {'|Obs_L|':>10} {'manuscript':>11} {'match':>6}", end="")
    print(f" {'cross-check':>12}" if cross_check else "")

    all_ok = True
    for L in range(L_lo, L_hi + 1):
        mine = obstructions(L)
        n = len(mine)
        expected = MANUSCRIPT_COUNTS.get(L)
        tab_ok = expected is None or n == expected
        all_ok &= tab_ok
        line = f"  {L:>3} {n:>10} {str(expected):>11} {('OK' if tab_ok else 'FAIL'):>6}"
        if cross_check:
            # Element-wise set comparison against the canonical enumerator.
            total, _, _, _, obs_list, _ = count_obstructions.count_at(L, atoms=False)
            set_ok = (obs_list == mine) and (total == n)
            all_ok &= set_ok
            line += f" {('SETS EQUAL' if set_ok else 'SETS DIFFER'):>12}"
        print(line)

    if not all_ok:
        print("MISMATCH DETECTED", file=sys.stderr)
        sys.exit(1)
    print("# all checks passed")


if __name__ == "__main__":
    main()
