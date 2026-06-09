#!/usr/bin/env python3
"""Negative-shift tails |s| in {2,3} closed for ALL q via a bounded carry
automaton (`lem:carry-automaton`); the mirror of the positive s=2 case.

After the necessary condition (N) 3^{J+1} > 2^{J+2|s|} (depth_bound_threshold.py)
the only open negative strata are (a=|s|, J): (2,5), (2,6), (3,8). For each we
must show no obstruction exists for ANY q.

Encoding (sign-free identity, explicit bit placement):
    sum_{j=0}^J 3^{J-j} 2^{V_K^j}  -  2^v sum_{j=0}^J 3^{J-j} 2^{V_I^j}  -  3^{J+1}  =  0,
with V_K^j increasing (prefix V_K^j=j for j<=v-1, gap V_K^v>=v+1), V_I^j
increasing, terminals V_K^J = J+q+v-2a, V_I^J = J+q. Reading bit positions p:
a K-exponent of index jK sits at p = V_K^jK (coeff +3^{J-jK}); an I-exponent of
index jI sits at p = V_I^jI + v (coeff -3^{J-jI}); -3^{J+1} injected at p=0.
State (carry, jK, jI), carry bounded. q only stretches block A and shifts the
terminal block B (width 2a+1). Block-A reachability R_m = T_A^m(R0) is eventually
periodic -> all q decided by a finite preperiod + one period.

Streams: validation against the trajectory oracle, the known tight obstruction
r=1015979 as a nonzero guard, a finite cross-check, then the all-q fixed-point
verdict per stratum. Exits non-zero unless the exact DP matches the oracle, the
tight guard is nonzero, the DP is 0 across the open strata, and the fixed point
rejects for all q.
"""
import sys
from functools import lru_cache
from collections import Counter


def v2(n):
    return (n & -n).bit_length() - 1


# ---------- trajectory oracle (independent, integer) ----------
def reduce_full(r, L):
    if r & 1 == 0 or r == 1:
        return None
    v = v2(r - 1)
    if not (1 <= v < L):
        return None
    aK, aI = r, (r - 1) >> v
    VK, VI = [0], [0]
    while True:
        vK, vI = v2(3 * aK - 1), v2(3 * aI - 1)
        if vK >= L - VK[-1] or vI >= (L - v) - VI[-1]:
            delta = VK[-1] - VI[-1] - v
            if delta >= 0:
                X1 = (3 * aI == (1 << delta) * (3 * aK - 1) + 1)
            else:
                e = -delta
                X1 = ((1 << e) * 3 * aI == (3 * aK - 1) + (1 << e))
            if not X1 or delta % 2:
                return None
            return delta // 2, len(VK) - 1, v, VK[-1], VI[-1]
        aK, aI = (3 * aK - 1) >> vK, (3 * aI - 1) >> vI
        VK.append(VK[-1] + vK)
        VI.append(VI[-1] + vI)


# ---------- exact carry DP (polynomial in q; for validation + base cases) ----------
def neg_carry_dp(a, J, v, q):
    """# obstructions with shift s=-a, depth J, given v and q."""
    tVK, tVI = J + q + v - 2 * a, J + q
    if v < 1 or tVK < J or tVI < J:
        return 0
    if v > J:
        # prefix forces V_K^j=j for all j<=J, so V_K^J=J, i.e. tVK=J -> q=2a-v<0 for J>2a: empty
        return 0
    AB = 3 ** (J + 1)
    Pmax = tVI + v + 1

    @lru_cache(maxsize=None)
    def go(p, carry, jK, jI):
        if p > Pmax:
            return 1 if (carry == 0 and jK == J + 1 and jI == J + 1) else 0
        if jK <= v - 1:
            Kopt = [1] if p == jK else [0]            # forced prefix (incl. j=0 at 0)
        elif jK == J:
            Kopt = [1] if p == tVK else [0]           # terminal K
        elif v <= jK <= J - 1 and p < tVK and (jK > v or p >= v + 1):
            Kopt = [0, 1]                              # free K
        else:
            Kopt = [0]
        if jI == 0:
            Iopt = [1] if p == v else [0]             # V_I^0 = 0 -> position v
        elif jI == J:
            Iopt = [1] if p == tVI + v else [0]        # terminal I
        elif 1 <= jI <= J - 1 and v + 1 <= p < tVI + v:
            Iopt = [0, 1]                              # free I
        else:
            Iopt = [0]
        kcoef = 3 ** (J - jK) if jK <= J else 0
        icoef = 3 ** (J - jI) if jI <= J else 0
        tot = 0
        for pk in Kopt:
            for pi in Iopt:
                digit = carry + pk * kcoef - pi * icoef - (AB if p == 0 else 0)
                if digit & 1:
                    continue
                tot += go(p + 1, digit >> 1, jK + pk, jI + pi)
        return tot

    r = go(0, 0, 0, 0)
    go.cache_clear()
    return r


# ---------- all-q fixed point (block-A reachability) ----------
def neg_all_q(a, J, v):
    """Return (M0, P, has_obstruction_for_some_q, n_states) for shift s=-a, depth J, param v."""
    if v < 1 or v > J:
        # v>J: prefix forces V_K^J=J => tVK=J => q=2a-v<0 for J>2a: no obstruction
        return (None, None, False, 0)
    AB = 3 ** (J + 1)

    # R0: deterministic state after positions 0..v (forced prefix + I_0), entering block A at p=v+1.
    carry, jK, jI = 0, 0, 0
    for p in range(0, v + 1):
        digit = carry - (AB if p == 0 else 0)
        if jK <= v - 1 and p == jK:            # forced prefix K
            digit += 3 ** (J - jK)
            jK += 1
        if jI == 0 and p == v:                 # forced I_0 at position v
            digit -= 3 ** (J - 0)
            jI += 1
        if digit & 1:
            return (None, None, False, 0)       # R0 infeasible -> no obstruction
        carry = digit >> 1
    R0 = frozenset({(carry, jK, jI)})          # jK=v, jI=1 expected

    def TA(S):                                  # one block-A position: free K and/or free I, no special bit
        out = set()
        for (c, jk, ji) in S:
            Kopt = [0, 1] if v <= jk <= J - 1 else [0]
            Iopt = [0, 1] if 1 <= ji <= J - 1 else [0]
            for pk in Kopt:
                for pi in Iopt:
                    d = c + pk * 3 ** (J - jk) - pi * 3 ** (J - ji)
                    if d & 1:
                        continue
                    out.add((d >> 1, jk + pk, ji + pi))
        return frozenset(out)

    seq, seen = [R0], {R0: 0}
    while True:
        nxt = TA(seq[-1])
        if nxt in seen:
            M0, P = seen[nxt], len(seq) - seen[nxt]
            break
        seen[nxt] = len(seq)
        seq.append(nxt)

    def block_B(S):                             # positions tVK..tVI+v (local 0..2a), q-independent
        for local in range(2 * a + 1):
            out = set()
            for (c, jk, ji) in S:
                place_termK = (local == 0)
                place_termI = (local == 2 * a)
                jk2, dK, okK = jk, c, True
                if place_termK:
                    if jk != J:
                        okK = False
                    else:
                        dK = c + 3 ** (J - J)
                        jk2 = J + 1
                if not okK:
                    continue
                if place_termI:
                    Iopt = [('T',)]
                else:
                    Iopt = [('none',)] + ([('freeI',)] if 1 <= ji <= J - 1 else [])
                for opt in Iopt:
                    d = dK
                    ji2 = ji
                    if opt == ('T',):
                        if ji != J:
                            continue
                        d -= 3 ** (J - J)
                        ji2 = J + 1
                    elif opt == ('freeI',):
                        d -= 3 ** (J - ji)
                        ji2 = ji + 1
                    if d & 1:
                        continue
                    out.add((d >> 1, jk2, ji2))
            S = frozenset(out)
        return S

    def accepts_from(S):
        return any(c == 0 and jk == J + 1 and ji == J + 1 for (c, jk, ji) in block_B(S))

    # block-A length = tVK-1-v = J+q-2a-1; reachable set after block A is R_m with m=J+q-2a-1.
    # cover preperiod + one period of m -> all q >= 0 with m >= 0.
    bad = []
    for m in range(M0 + P + 1):
        q = m + 2 * a + 1 - J            # m = J+q-2a-1  =>  q = m - J + 2a + 1
        if q < 0:
            continue
        Rm = seq[m] if m < len(seq) else seq[M0 + ((m - M0) % P)]
        if accepts_from(Rm):
            bad.append(q)
    n_states = len(set().union(*seq))            # block-A reachable state-space size
    return (M0, P, bool(bad), n_states)


def main():
    print("== 1. validate exact carry-DP vs trajectory oracle (s<0, L=11..18) ==", flush=True)
    mism = nz = 0
    for L in range(11, 19):
        cnt = Counter()
        for r in range(3, (1 << L) + 1, 2):
            res = reduce_full(r, L)
            if res is None:
                continue
            s, J, v, VKJ, VIJ = res
            if s < 0:
                a = -s
                q = VIJ - J
                cnt[(a, J, v, q)] += 1
        for (a, J, v, q), c in cnt.items():
            dp = neg_carry_dp(a, J, v, q)
            if dp != c:
                mism += 1
                if mism <= 5:
                    print(f"   MISMATCH a={a},J={J},v={v},q={q}: oracle={c} dp={dp}", flush=True)
            if c > 0:
                nz += 1
        print(f"   L={L}: {sum(cnt.values())} neg-shift obstr, {len(cnt)} (a,J,v,q)-cells checked", flush=True)
    print(f"   mismatches={mism}; nonzero cells validated={nz}", flush=True)

    print("== 2. guard: exact DP must be NONZERO on the known tight obstruction (a=2,J=7,v=1,q=12) ==", flush=True)
    g = neg_carry_dp(2, 7, 1, 12)
    print(f"   neg_carry_dp(a=2,J=7,v=1,q=12) = {g}  (must be >=1; r=1015979)", flush=True)

    print("== 3. finite cross-check: exact DP == 0 on the open strata, q=0..40, v=1..J ==", flush=True)
    strata = [(2, 5), (2, 6), (3, 8)]
    Qx = 40
    nz_total = 0
    for (a, J) in strata:
        n = sum(neg_carry_dp(a, J, v, q) for v in range(1, J + 1) for q in range(0, Qx + 1))
        nz_total += n
        print(f"   (|s|={a}, J={J}): nonzero obstruction counts over q<=Qx = {n}", flush=True)

    print("== 4. all-q fixed-point verdict on the open strata (a,J): (2,5),(2,6),(3,8) ==", flush=True)
    proven = True
    for (a, J) in strata:
        any_bad = False
        M0max = Pmax = nsmax = 0
        for v in range(1, J + 1):            # v>J is empty (prefix forces V_K^J=J, q=2a-v<0 for J>2a)
            M0, P, bad, ns = neg_all_q(a, J, v)
            if M0 is not None:
                M0max = max(M0max, M0)
                Pmax = max(Pmax, P)
                nsmax = max(nsmax, ns)
                print(f"   |s|={a},J={J},v={v}: preperiod M0={M0}, period P={P}, "
                      f"block-A states={ns} -> {'reject all q' if not bad else f'CANDIDATE q={bad}'}",
                      flush=True)
            if bad:
                any_bad = True
        status = "NO obstruction for any q (all v<=J)" if not any_bad else "CANDIDATES FOUND"
        print(f"   stratum (|s|={a}, J={J}): {status}  (max M0={M0max}, max P={Pmax}, max states={nsmax})",
              flush=True)
        proven &= not any_bad

    verdict = (mism == 0 and g >= 1 and nz_total == 0 and proven)
    print(f"\n*** negative tails |s| in {{2,3}} closed for all q: {verdict} "
          f"=> with |s|>=4 (analytic) and the (N)-reduction, negative-shift J>=2|s|+3 PROVEN ***",
          flush=True)
    assert mism == 0, "exact DP disagrees with the trajectory oracle"
    assert g >= 1, "tight-obstruction guard failed (DP counts 0 where r=1015979 exists)"
    assert nz_total == 0, "exact DP found an obstruction in an open stratum"
    assert proven, "fixed point admits an accepting run for some q"
    sys.exit(0)


if __name__ == "__main__":
    main()
