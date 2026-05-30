"""Shared parallel-reduction core for the obstruction_residues_family checks.

Single source of the T_{a,c}(n) = (a n + c)/2^{v_2(a n + c)} parallel
reduction, factored out of notes/scripts/count_obstructions_ac.py so the
per-asset checks agree on one implementation. Each check imports from
here; verify.py runs the checks with cwd = instance dir, so the checks/
directory (this file) is on sys.path automatically.

Notation matches the manuscript: an obstruction residue r at level L
reduces in J steps to a terminal datum; the shift index is
delta_J = V_K - V_I - v, and (order lemma) e = ord_{|a|}(2) divides it.
"""

from fractions import Fraction


def v2(n: int) -> int:
    if n == 0:
        return 10**9
    n = abs(n)
    c = 0
    while n & 1 == 0:
        n >>= 1
        c += 1
    return c


def ord2(a: int) -> int:
    """Multiplicative order e = ord_{|a|}(2) (a odd, |a| > 1; 1 for |a|=1)."""
    a = abs(a)
    if a == 1:
        return 1
    k, x = 1, 2 % a
    while x != 1:
        x = (x * 2) % a
        k += 1
    return k


class Endpoint:
    __slots__ = ("coef", "dval", "J", "V_K", "V_I", "v")

    def __init__(self, coef, dval, J, V_K, V_I, v):
        self.coef = coef   # c_J  (Fraction)
        self.dval = dval   # d_J  (Fraction)
        self.J = J         # termination index
        self.V_K = V_K     # cumulative K valuation at termination
        self.V_I = V_I     # cumulative I valuation at termination
        self.v = v         # initial 2-adic valuation v_2(r + c)


def reduce(r: int, L: int, a: int, c: int):
    """Parallel reduction of residue r at level L for T_{a,c}.

    Returns an Endpoint at termination, or None if r is ineligible
    (even r, even/zero c or a, r + c == 0, or v out of range).
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
    a_K, b_K = r, 1 << L
    a_I, b_I = s // factor, 1 << (L - v)
    coef = Fraction(1, factor)
    dval = Fraction(c, factor)
    V_K = V_I = J = 0
    while True:
        A_K = a * a_K + c
        A_I = a * a_I + c
        v_K = v2(A_K)
        v_I = v2(A_I)
        if v_K >= v2(b_K) or v_I >= v2(b_I):
            return Endpoint(coef, dval, J, V_K, V_I, v)
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


def cumulative_trace(r: int, L: int, a: int, c: int):
    """For an eligible r, return (snaps, v) where snaps[j] = (V_K^{(j)},
    V_I^{(j)}) is the cumulative valuation pair after j reduction steps,
    j = 0..J (snaps[0] = (0, 0)). Used by the diophantine-identity check
    (X_j = 2^{V_K^{(j)}} - 2^{V_I^{(j)} + v}). None if r is ineligible."""
    if r % 2 == 0 or c == 0 or c % 2 == 0 or a % 2 == 0:
        return None
    s = r + c
    if s == 0:
        return None
    v = v2(s)
    if v <= 0 or v >= L:
        return None
    factor = 1 << v
    a_K, b_K = r, 1 << L
    a_I, b_I = s // factor, 1 << (L - v)
    V_K = V_I = 0
    snaps = [(0, 0)]
    while True:
        A_K = a * a_K + c
        A_I = a * a_I + c
        v_K = v2(A_K)
        v_I = v2(A_I)
        if v_K >= v2(b_K) or v_I >= v2(b_I):
            return (snaps, v)
        a_K = A_K >> v_K
        b_K = (a * b_K) >> v_K
        a_I = A_I >> v_I
        b_I = (a * b_I) >> v_I
        V_K += v_K
        V_I += v_I
        snaps.append((V_K, V_I))


def is_obstruction(ep, a: int, c: int) -> bool:
    if ep is None:
        return False
    return c * (1 - ep.coef) + a * ep.dval == 0


def shift_index(ep, a: int):
    """delta_J / e; None if e does not divide delta_J (order-lemma violation)."""
    if ep is None:
        return None
    delta = ep.V_K - ep.V_I - ep.v
    e = ord2(a)
    if delta % e != 0:
        return None
    return delta // e


def obstructions(L: int, a: int, c: int):
    """All (r, endpoint) with r an obstruction residue at level L."""
    out = []
    for r in range(1, 1 << L, 2):
        ep = reduce(r, L, a, c)
        if is_obstruction(ep, a, c):
            out.append((r, ep))
    return out


def is_atomic(r: int, L: int, a: int, c: int) -> bool:
    """r in O_L is atomic iff its projection r mod 2^{L-1} is NOT in O_{L-1}
    (otherwise r is a lift of that lower-level obstruction)."""
    if L <= 1:
        return True
    proj = r % (1 << (L - 1))
    return not is_obstruction(reduce(proj, L - 1, a, c), a, c)


def sync_level(r: int, L: int, a: int, c: int):
    """Sync stage k = number of leading non-zero X_j (X_j = 2^{V_K^{(j)}} -
    2^{V_I^{(j)}+v}); equivalently J+1 minus the trailing run of zero X_j.
    Main class -> k=1, atoms -> k>=2. None if r is ineligible."""
    ct = cumulative_trace(r, L, a, c)
    if ct is None:
        return None
    snaps, v = ct
    xs = [(1 << vk) - (1 << (vi + v)) for (vk, vi) in snaps]
    z = 0
    for x in reversed(xs):
        if x == 0:
            z += 1
        else:
            break
    return len(xs) - z


if __name__ == "__main__":
    # Self-test: negative-Mersenne enumeration (a = -q), not part of a check.
    for q in (3, 7, 15):
        a = -q
        cnt = sum(len(obstructions(L, a, 1)) for L in range(3, 11))
        print(f"q={q} (a={a}): |O| L=3..10 = {cnt}")
