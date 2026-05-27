"""Hindernis-Theorie fuer die Familie T_{a,c}(n) = (a n + c) / 2^{v_2(a n + c)}.

Generalisiert count_obstructions_generic.py auf einen weiteren Parameter a
(ungerade) statt a=3 fest. Setup: m := (r + c)/2^v mit v := v_2(r + c).
Update: c_{j+1} = c_j * 2^{v_K - v_I},
        d_{j+1} = (a d_j + c(1 - c_j)) / 2^{v_I}.
Hindernis: c(1 - c_J) + a d_J = 0.

Wird primaer fuer (a=1, c=+/-1) genutzt — die "1n+1" / "1n-1"-Faelle, die
strukturell deutlich einfacher sein sollten als a=3.
"""

import sys
from fractions import Fraction


def v2(n):
    if n == 0:
        return 10**9
    n = abs(n)
    cnt = 0
    while (n & 1) == 0:
        n >>= 1
        cnt += 1
    return cnt


def parallel_reduce(r, L, a, c, return_J=False):
    """Parallel reduction for T_{a,c} starting from r at level L.

    Returns (c_J, d_J, V_K, V_I, v) at termination, or None if r is ineligible.
    With return_J=True the termination index J (number of completed steps) is
    appended: (c_J, d_J, V_K, V_I, v, J). The default 5-tuple form is kept so
    existing callers (is_obstruction, shift_index, downstream importers) are
    unaffected.
    """
    if r % 2 == 0 or c == 0 or c % 2 == 0 or a % 2 == 0:
        return None
    s = r + c
    if s == 0:
        return None
    v = v2(s)
    if v <= 0 or v >= L:
        return None
    factor = 1 << v
    m = s // factor
    a_K, b_K = r, 1 << L
    a_I, b_I = m, 1 << (L - v)
    coef = Fraction(1, factor)
    dval = Fraction(c, factor)
    V_K = 0
    V_I = 0
    J = 0

    while True:
        A_K = a * a_K + c
        A_I = a * a_I + c
        v_K = v2(A_K)
        v_I = v2(A_I)
        v_bK = v2(b_K)
        v_bI = v2(b_I)
        if v_K >= v_bK or v_I >= v_bI:
            return (coef, dval, V_K, V_I, v, J) if return_J else (coef, dval, V_K, V_I, v)

        coef_old = coef
        coef = coef_old * Fraction(1 << v_K, 1 << v_I)
        dval = (a * dval + c * (1 - coef_old)) / Fraction(1 << v_I)
        a_K = A_K >> v_K
        b_K = (a * b_K) >> v_K
        a_I = A_I >> v_I
        b_I = (a * b_I) >> v_I
        V_K += v_K
        V_I += v_I
        J += 1


def is_obstruction(endpoint, a, c):
    if endpoint is None:
        return False
    coef, dval = endpoint[0], endpoint[1]
    return c * (1 - coef) + a * dval == 0


def ord2(n):
    """Multiplicative order e = ord_{|n|}(2) of 2 modulo |n| (n odd)."""
    n = abs(n)
    if n == 1:
        return 1
    k, x = 1, 2 % n
    while x != 1:
        x = (x * 2) % n
        k += 1
    return k


def shift_index(endpoint, a):
    """Shift class s = delta_J / e with e := ord_{|a|}(2) (order lemma).

    Returns None when delta_J is not divisible by e -- an order-lemma
    violation. For a = 3 this reduces to the parity lemma (e = 2)."""
    if endpoint is None:
        return None
    V_K, V_I, v = endpoint[2], endpoint[3], endpoint[4]
    delta = V_K - V_I - v
    e = ord2(a)
    if delta % e != 0:
        return None
    return delta // e


def enumerate_obstructions(L, a, c):
    obs = []
    for r in range(1, 1 << L, 2):
        endpoint = parallel_reduce(r, L, a, c)
        if is_obstruction(endpoint, a, c):
            shift = shift_index(endpoint, a)
            obs.append((r, shift, endpoint))
    return obs


def atom_j_stats(L, a, c):
    """Termination-index statistics over atomic shift-nonzero obstructions.

    An obstruction r at level L is atomic iff r mod 2^{L-1} is not an
    obstruction at level L-1; "shift-nonzero" excludes the G_0 class. Returns
    (count, J_min, J_max, mean_J), reproducing the columns of the manuscript's
    J-statistics table (tab:J-stats / tab:Jmax-a). By the no-shift-zero-atom
    theorem every atom is shift-nonzero, so the count equals |Atom_L|.
    """
    prev = {r for r, _, _ in enumerate_obstructions(L - 1, a, c)}
    half = 1 << (L - 1)
    js = []
    for r in range(1, 1 << L, 2):
        ep = parallel_reduce(r, L, a, c, return_J=True)
        if not is_obstruction(ep, a, c):
            continue
        if shift_index(ep, a) in (None, 0):
            continue
        if (r % half) in prev:
            continue  # non-atomic: a lift of a level-(L-1) obstruction
        js.append(ep[5])
    if not js:
        return (0, None, None, None)
    return (len(js), min(js), max(js), sum(js) / len(js))


def main():
    L_max = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    pairs = [(1, 1), (1, -1), (3, 1), (3, -1), (5, 1), (5, -1), (7, 1), (7, -1),
             (9, -1), (15, -1), (21, -1), (31, -1)]
    print(f"# |Obs_L^(a,c)| for L = 4 .. {L_max}")
    print()
    header = ["(a,c)"] + [f"L={L}" for L in range(4, L_max + 1)] + [f"density(L={L_max})"]
    print(" | ".join(header))
    print(" | ".join(["---"] * len(header)))
    counts_table = {}
    for (a, c) in pairs:
        row = [f"({a:+d},{c:+d})"]
        counts_by_L = {}
        for L in range(4, L_max + 1):
            obs = enumerate_obstructions(L, a, c)
            counts_by_L[L] = len(obs)
            row.append(f"{len(obs)}")
        density = counts_by_L[L_max] / (1 << L_max)
        row.append(f"{density:.5f}")
        print(" | ".join(row))
        counts_table[(a, c)] = counts_by_L

    print()
    print(f"# Shift-index breakdown at L = {L_max}")
    print()
    print("(a,c) | total | G_0 | G_>0 | G_<0 | order-violation")
    print("---|---|---|---|---|---")
    for (a, c) in pairs:
        obs = enumerate_obstructions(L_max, a, c)
        total = len(obs)
        g_0 = sum(1 for _, s, _ in obs if s == 0)
        g_pos = sum(1 for _, s, _ in obs if s is not None and s > 0)
        g_neg = sum(1 for _, s, _ in obs if s is not None and s < 0)
        g_none = sum(1 for _, s, _ in obs if s is None)
        print(f"({a:+d},{c:+d}) | {total} | {g_0} | {g_pos} | {g_neg} | {g_none}")

    print()
    print("# Termination-index statistics for atomic G_!=0 obstructions, a=3, c=-1")
    print("# (reproduces tab:J-stats; J_max = L-4 for even L is Theorem L-4-family)")
    print()
    print("L | |Atom| | J_min | J_max | mean_J")
    print("---|---|---|---|---")
    for L in range(10, min(L_max, 14) + 1, 2):
        cnt, jmin, jmax, jbar = atom_j_stats(L, 3, -1)
        jbar_s = f"{jbar:.2f}" if jbar is not None else "---"
        print(f"{L} | {cnt} | {jmin} | {jmax} | {jbar_s}")

    print()
    print(f"# Atomic J_max across |a| at L = {min(L_max, 14)} (cf. tab:Jmax-a)")
    print()
    print("a | e | J_max | L - J_max")
    print("---|---|---|---")
    L_jmax = min(L_max, 14)
    for a in (3, 5, 7):
        _, _, jmax, _ = atom_j_stats(L_jmax, a, -1)
        if jmax is None:
            print(f"{a} | {ord2(a)} | --- | ---")
        else:
            print(f"{a} | {ord2(a)} | {jmax} | {L_jmax - jmax}")

    print()
    print(f"# First obstructions for (a=1, c=+1) at L = 6 .. min({L_max},10)")
    print()
    for L in range(6, min(L_max, 10) + 1):
        obs = enumerate_obstructions(L, 1, 1)
        if obs:
            rs = sorted(r for r, _, _ in obs)
            print(f"L={L}: |Obs|={len(obs)}, first few: {rs[:10]}")
        else:
            print(f"L={L}: |Obs|=0")

    print()
    print(f"# First obstructions for (a=1, c=-1) at L = 6 .. min({L_max},10)")
    print()
    for L in range(6, min(L_max, 10) + 1):
        obs = enumerate_obstructions(L, 1, -1)
        if obs:
            rs = sorted(r for r, _, _ in obs)
            print(f"L={L}: |Obs|={len(obs)}, first few: {rs[:10]}")
        else:
            print(f"L={L}: |Obs|=0")


if __name__ == "__main__":
    main()
