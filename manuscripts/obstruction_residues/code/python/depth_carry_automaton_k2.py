#!/usr/bin/env python3
"""Positive shift s=2 tail (J=6) closed for ALL q via a bounded carry automaton
(`lem:carry-automaton`).

Statement: no obstruction residue with s=2, J=6 exists, for any q>=0 and any
v in {1,...,6}. With the closed-form bound ruling out J<=5 for s=2
(`lem:depth-posbig`), every s=2 obstruction has J >= 7 = 2s+3.

Why this is a proof, not a q-enumeration
----------------------------------------
The obstruction condition for (s=2, J=6, v, q) is equivalent to the integer
equation (sign-free identity read as a bit-position recursion)

   sum_{i=1..5} 3^{5-i} 2^{f_i}  -  sum_{j=v..5} 3^{5-j} 2^{g_j}  +  C
        = 2^{6+q} + 2^{8+q},      C = 3^{6-v} + 3^5,            (**)

   1 <= f_1 < ... < f_5 <= 5+q          (I-track exponents V_I^{(i)})
   1 <= g_v < ... < g_5 <= 9+q          (K-track free exponents V_K^{(j)} - v)

Solutions of (**) are recognised by a finite carry automaton reading bit
positions p = 0,1,2,...: state = (carry, #f placed, #g placed); the carry is
bounded by sum|coeff|; at each position the placed terms must keep the emitted
bit 0; accept iff at the end carry=0 and all f,g placed. The number of accepting
paths is exactly the obstruction count (validated below against the brute
(v_K,v_I)-DFS, on zero AND nonzero targets, so the automaton genuinely counts).

The only q-dependence is (i) the two 1-bits at 6+q, 8+q and (ii) the eligibility
windows (f <= 5+q, g <= 9+q). This splits a run into BLOCK A = positions 1..5+q
(f+g eligible, no 1-bit; one fixed transition T_A) followed by the FIXED
4-position BLOCK B = 6+q..9+q (g-only; 1-bits at local 0 and 2). The
reachable-state sequence R_m = T_A^m(R0) is eventually periodic (finite state
space) and here reaches a fixed point (period 1) after a small preperiod M0, for
every v. From that fixed point block B has no accepting path, so the automaton
rejects for all large q; the finitely many smaller q are checked directly. Hence
(**) has no solution for ANY q -- a bounded computation, not a q-loop.

Exits non-zero unless: the carry-DP matches the brute DFS on all sampled
targets, every v reaches a rejecting fixed point, and the exact DP is 0 on the
target across a finite q-window.
"""
import sys
from functools import lru_cache

sys.setrecursionlimit(10 ** 6)


def carry_dp(v, q, D=-5):
    """Exact obstruction count for (s=2, J=6, v, q) with target d_J = D.
    Polynomial in q (bounded carry); used for validation and small-q base cases."""
    Icoef = [81, 27, 9, 3, 1]
    Kcoef = [3 ** (5 - j) for j in range(v, 6)]
    nK = len(Kcoef)
    C = 3 ** (6 - v) + 3 ** 5
    f_hi, g_hi = 5 + q, 9 + q
    top = set()
    negD = -D
    b = 0
    while negD > 0:
        if negD & 1:
            top.add(6 + q + b)
        negD >>= 1
        b += 1
    Pmax = max((max(top) if top else 0), 8 + q, f_hi, g_hi) + 4

    @lru_cache(maxsize=None)
    def go(p, carry, fi, gj):
        if p > Pmax:
            return 1 if (carry == 0 and fi == 5 and gj == nK) else 0
        base = carry + (C if p == 0 else 0) - (1 if p in top else 0)
        c = 0
        for pf in ((0, 1) if (fi < 5 and 1 <= p <= f_hi) else (0,)):
            for pg in ((0, 1) if (gj < nK and 1 <= p <= g_hi) else (0,)):
                tot = base + (Icoef[fi] if pf else 0) - (Kcoef[gj] if pg else 0)
                if tot & 1:
                    continue
                c += go(p + 1, tot >> 1, fi + pf, gj + pg)
        return c

    r = go(0, 0, 0, 0)
    go.cache_clear()
    return r


def dfs_count(v, q, D=-5, M=6, k=2):
    """Brute (v_K, v_I)-sequence DFS (the project's accepted coupled method); the oracle."""
    tVK, tVI = M + 2 * k + v + q, M + q
    vK_max = max(2, tVK - (M - 1))
    vI_max = max(1, tVI - (M - 1))
    denom = 1 << (v + M + q)
    cnt = [0]

    def dfs(j, sK, sI, VK, VI, nt):
        if j == M:
            if sK == tVK and sI == tVI and nt % denom == 0 and nt // denom == D:
                cnt[0] += 1
            return
        rK, rI, rs = tVK - sK, tVI - sI, M - j
        if rK < rs or rI < rs or rK > rs * vK_max or rI > rs * vI_max:
            return
        if j == 0:
            opt = [1] if v >= 2 else range(2, vK_max + 1)
        elif j < v - 1:
            opt = [1]
        elif j == v - 1 and v >= 2:
            opt = range(2, vK_max + 1)
        else:
            opt = range(1, vK_max + 1)
        for a in opt:
            if a > rK:
                break
            for b in range(1, vI_max + 1):
                if b > rI:
                    break
                dfs(j + 1, sK + a, sI + b, VK + a, VI + b,
                    3 * nt + (1 << VK) - (1 << (v + VI)))

    dfs(0, 0, 0, 0, 0, -1)
    return cnt[0]


def symbolic_all_q(v):
    """q-symbolic proof for one v: returns (M0, P, bad_qs). bad_qs empty => no
    obstruction for ANY q (target d_J = -5)."""
    Icoef = [81, 27, 9, 3, 1]
    Kcoef = [3 ** (5 - j) for j in range(v, 6)]
    nK = len(Kcoef)
    C = 3 ** (6 - v) + 3 ** 5
    assert C % 2 == 0
    R0 = frozenset({(C // 2, 0, 0)})  # state entering block A (position 0 added C)

    def TA(S):  # one block-A position: f+g eligible, no 1-bit
        out = set()
        for (carry, fi, gj) in S:
            for pf in ((0, 1) if fi < 5 else (0,)):
                for pg in ((0, 1) if gj < nK else (0,)):
                    tot = carry + (Icoef[fi] if pf else 0) - (Kcoef[gj] if pg else 0)
                    if tot & 1:
                        continue
                    out.add((tot >> 1, fi + pf, gj + pg))
        return frozenset(out)

    seq, seen = [R0], {R0: 0}
    while True:
        nxt = TA(seq[-1])
        if nxt in seen:
            M0, P = seen[nxt], len(seq) - seen[nxt]
            break
        seen[nxt] = len(seq)
        seq.append(nxt)

    def block_B(S):  # positions 6+q..9+q: g-only; 1-bits at local 0 and 2
        for local in range(4):
            is_top = local in (0, 2)
            out = set()
            for (carry, fi, gj) in S:
                base = carry - (1 if is_top else 0)
                for pg in ((0, 1) if gj < nK else (0,)):
                    tot = base - (Kcoef[gj] if pg else 0)
                    if tot & 1:
                        continue
                    out.add((tot >> 1, fi, gj + pg))
            S = frozenset(out)
        return S

    def R_afterA(q):
        m = 5 + q
        return seq[m] if m < len(seq) else seq[M0 + ((m - M0) % P)]

    def accepts(q):
        S = frozenset((c, fi, gj) for (c, fi, gj) in R_afterA(q) if fi == 5)
        return any(c == 0 and fi == 5 and gj == nK for (c, fi, gj) in block_B(S))

    bad = [q for m in range(M0 + P) for q in (m - 5,) if q >= 0 and accepts(q)]
    return M0, P, bad


def main():
    print("== 1. validate carry-DP == brute coupled DFS on targets WITH solutions ==", flush=True)
    ok = True
    nz = False
    for D in (-1, -3, -4, -6):
        for v in range(1, 7):
            for q in range(0, 7):
                a, b = carry_dp(v, q, D), dfs_count(v, q, D)
                ok &= (a == b)
                nz |= (b > 0)
    print(f"   match on all (D,v,q): {ok}; saw nonzero counts: {nz}", flush=True)

    print("== 2. q-symbolic proof: obstruction (d_J=-5) count is 0 for ALL q ==", flush=True)
    proven = True
    for v in range(1, 7):
        M0, P, bad = symbolic_all_q(v)
        print(f"   v={v}: block-A fixed point at preperiod M0={M0} (period {P}); "
              f"{'NO obstruction for all q' if not bad else f'CANDIDATES q={bad}'}", flush=True)
        proven &= not bad

    print("== 3. cross-check exact carry-DP == 0 (s=2, J=6, all v, q=0..30) ==", flush=True)
    mism = sum(1 for v in range(1, 7) for q in range(0, 31) if carry_dp(v, q) != 0)
    print(f"   nonzero counts found: {mism}", flush=True)

    verdict = ok and nz and proven and mism == 0
    print(f"\n*** s=2 tail (J=6): {'CLOSED for all q, all v (=> J>=2s+3)' if verdict else 'NOT closed'} ***",
          flush=True)
    assert ok, "carry-DP disagrees with the coupled DFS oracle"
    assert nz, "DFS oracle never produced a nonzero count (validation vacuous)"
    assert proven, "some v admits an accepting run for some q"
    assert mism == 0, "exact DP found a nonzero obstruction count on the target"
    sys.exit(0)


if __name__ == "__main__":
    main()
