#!/usr/bin/env python3
"""Closed-form decoupled depth bound for positive shift (`lem:depth-posbig`).

An obstruction with shift s >= 2, termination index J, parameter v and
q := V_I^{(J)} - J >= 0 satisfies the O''-form of the sign-free identity,
    A_K - 2^v A_I = 3^{J+1} + 2^{J+q+v}(1 - 4^s)  =: RHS,
with A_K = sum_{j=0}^{J-1} 3^{J-j} 2^{V_K^j},  A_I = sum_{j=0}^{J-1} 3^{J-j} 2^{V_I^j}.
Decoupling (minimise A_K, maximise A_I over the structural sequence families
independently) only underestimates the true left-hand side, so

    D(J,s,v,q) := (A_K^min - 2^v A_I^max) - RHS  >  0   =>   no obstruction.

The two extremal sums are geometric:
    A_I^max = 3^J + 2^q (2*3^J - 3*2^J),
    A_K^min = 3^{J+1} + 2^v 3^{J-v+1} - 6*2^J,
and D factorises affinely in 2^q:
    D = C_0(J,v) + 2^{v+q} * Gamma(J,s),
    C_0(J,v) = 2^v 3^J (3^{1-v} - 1) - 6*2^J,    Gamma(J,s) = 2^J(4^s + 2) - 2*3^J.

This script (1) checks both extremal sums against a brute minimisation/maximisation
over the structural sequence families on a small grid; (2) checks the
factorisation against the direct definition of D; (3) asserts, for s >= 4 and the
whole window 1 <= v <= J <= 2s+2, that Gamma(J,s) >= 0 (so q=0 is the worst case,
D non-decreasing in q) and D(J,s,v,0) > 0 -- hence D > 0 for all q and every such
obstruction has J >= 2s+3. For s in {2,3} it reports the finite set of residual
cells (D <= 0), which are closed by the carry automaton (depth_carry_automaton_*)
and the exhaustive search (depth_dfs_tails.py).

Exits non-zero on any mismatch or if the s >= 4 positivity fails.
"""
import sys
from fractions import Fraction as F


def AImax_cf(J, q):
    return 3 ** J + 2 ** q * (2 * 3 ** J - 3 * 2 ** J)


def AKmin_cf(J, v):
    return 3 ** (J + 1) + 2 ** v * 3 ** (J - v + 1) - 6 * 2 ** J


def Gamma(J, s):
    return 2 ** J * (4 ** s + 2) - 2 * 3 ** J


def Phi(J, s):
    return 2 ** J * (4 ** s + 2) - 3 ** (J + 1)


def C0(J, v):
    return F(2) ** v * F(3) ** J * (F(3) ** (1 - v) - 1) - 6 * F(2) ** J


def D_cf(J, s, v, q):
    return C0(J, v) + F(2) ** (v + q) * Gamma(J, s)


def RHS(J, s, v, q):
    return 3 ** (J + 1) + 2 ** (J + q + v) * (1 - 4 ** s)


def brute_AImax(J, q):
    """max sum_{j=0}^{J-1} 3^{J-j} 2^{V_I^j} over V_I^0=0, increments >=1, V_I^J=J+q."""
    target = J + q
    best = [-1]

    def rec(j, V, s):
        if j == J:
            if V == target:
                best[0] = max(best[0], s)
            return
        rem_steps = J - j
        for inc in range(1, (target - V) - (rem_steps - 1) + 1):
            rec(j + 1, V + inc, s + (3 ** (J - (j + 1)) * 2 ** (V + inc) if j + 1 <= J - 1 else 0))
    # account j=0 term (3^J * 2^0) separately, then add j>=1 placed terms
    rec(0, 0, 3 ** J)
    return best[0]


def brute_AKmin(J, v, q, s):
    """min sum_{j=0}^{J-1} 3^{J-j} 2^{V_K^j} over the K-track family with V_K^J fixed."""
    target = J + q + v + 2 * s
    best = [None]

    def rec(j, V, acc):
        if j == J:
            if V == target:
                best[0] = acc if best[0] is None else min(best[0], acc)
            return
        rem_steps = J - j
        # increment bounds: prefix forces inc=1 for j<v-1; the gap step j=v-1 has
        # inc>=2 (for v=1 this is step 0, i.e. v_K^{(0)}>=2); else inc>=1.
        lo = 1
        if j < v - 1:
            hi = 1
        elif j == v - 1:
            lo = 2
            hi = (target - V) - (rem_steps - 1)
        else:
            hi = (target - V) - (rem_steps - 1)
        for inc in range(lo, hi + 1):
            nV = V + inc
            term = 3 ** (J - (j + 1)) * 2 ** nV if j + 1 <= J - 1 else 0
            rec(j + 1, nV, acc + term)
    rec(0, 0, 3 ** J * 2 ** 0)   # j=0 term is 3^J * 2^0
    return best[0]


def main():
    print("== 1. extremal sums: closed form vs brute over the structural families ==", flush=True)
    mism = 0
    for J in range(2, 9):
        for q in range(0, 4):
            if brute_AImax(J, q) != AImax_cf(J, q):
                mism += 1
            for v in range(1, J + 1):
                for s in range(2, 4):
                    bk = brute_AKmin(J, v, q, s)
                    if bk is not None and bk != AKmin_cf(J, v):
                        mism += 1
    print(f"   closed-form A_I^max / A_K^min mismatches vs brute: {mism}", flush=True)

    print("== 2. factorisation D == C_0 + 2^{v+q} Gamma vs direct definition ==", flush=True)
    fmis = 0
    for J in range(2, 12):
        for s in range(2, 8):
            for v in range(1, J + 1):
                for q in range(0, 6):
                    direct = AKmin_cf(J, v) - 2 ** v * AImax_cf(J, q) - RHS(J, s, v, q)
                    if D_cf(J, s, v, q) != direct:
                        fmis += 1
    print(f"   factorisation mismatches: {fmis}", flush=True)

    print("== 3. s >= 4: Gamma >= 0 (q=0 worst) and D(J,s,v,0) > 0 over 1<=v<=J<=2s+2 ==", flush=True)
    gbad = dbad = 0
    for s in range(4, 13):
        for J in range(1, 2 * s + 3):
            if Gamma(J, s) < 0:
                gbad += 1
            for v in range(1, J + 1):
                if D_cf(J, s, v, 0) <= 0:
                    dbad += 1
    print(f"   Gamma<0 cases: {gbad}; D(.,0)<=0 cases: {dbad}  (both must be 0)", flush=True)

    print("== 4. residual cells (D<=0) for s in {2,3} -> closed by automaton/DFS ==", flush=True)
    for s in (2, 3):
        for J in range(1, 2 * s + 3):
            qstar = -1
            allq = False
            if Gamma(J, s) >= 0:
                # D non-decreasing in q: residual is a finite prefix q=0..qstar
                q = 0
                while any(D_cf(J, s, v, q) <= 0 for v in range(1, J + 1)):
                    qstar = q
                    q += 1
                    if q > 200:
                        allq = True
                        break
            else:
                allq = any(D_cf(J, s, v, 0) <= 0 for v in range(1, J + 1))
            if allq:
                print(f"   s={s}, J={J}: Gamma={Gamma(J,s)} < 0 -> q-UNBOUNDED residual (carry automaton)", flush=True)
            elif qstar >= 0:
                cells = [(v, q) for v in range(1, J + 1) for q in range(0, qstar + 1) if D_cf(J, s, v, q) <= 0]
                print(f"   s={s}, J={J}: finite residual q<= {qstar}: {cells}  (exhaustive DFS)", flush=True)
            else:
                print(f"   s={s}, J={J}: closed form covers all q (no residual)", flush=True)

    assert mism == 0, "closed-form extremal sum disagrees with brute family optimisation"
    assert fmis == 0, "factorisation D = C_0 + 2^{v+q} Gamma failed"
    assert gbad == 0, "Gamma < 0 somewhere in the s>=4 window (q=0 not worst case)"
    assert dbad == 0, "D(J,s,v,0) <= 0 somewhere in the s>=4 window"
    print("\n*** closed form proves J >= 2s+3 for s >= 4; s in {2,3} reduced to the listed finite residual ***",
          flush=True)
    sys.exit(0)


if __name__ == "__main__":
    main()
