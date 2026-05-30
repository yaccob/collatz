#!/usr/bin/env python3
"""Checks for thm_recursion, thm_node_lift, thm_stage4.

WHAT THIS CHECKS (exact rational arithmetic, concrete v_M)
  The sync recursion (thm_recursion): from (lambda_k, D_k),
      lambda_{k+1} = lambda_k * 2^{vI - vK},
      D_{k+1}      = (1 - lambda_k - q D_k) / 2^{vK},   lambda_0 = 2^{v0}, D_0 = -1,
  with sync (a_K = a_I) at (lambda, D) = (2^{j vM}, -(2^{j vM} - 1)/q).
  Running it on the documented valuation sequences must reach exactly that
  sync form for:
    - the four ITERATED node-lift families A_k, F1_k, B_k, C_k (j = 1),
      knoten_lift_theorem.py, k = 2..7;
    - the five UNIVERSAL stage-4 families A_lift, B_lift, C_lift, F1 (j = 1)
      and G1 (j = -1, rational sync), schema_stufe4_universell.py.

  The CONVERSE of thm_recursion ("the pre-synchronisation states are EXACTLY
  (2^{j vM}, -(2^{j vM}-1)/q), j in Z"): by direct enumeration (q in {3,7,15},
  L = 4..15) every obstruction's pre-sync lambda-exponent
  s = v0 + V_I^{(k-1)} - V_K^{(k-1)} is divisible by v_M -- for BOTH signs of s.
  This guards the negative-j (rational) half of the characterisation, which the
  forward family checks above do not touch; it also asserts that negative-j
  states actually occur, so the "j in Z, not N" claim is non-vacuous.

WHAT THIS DOES NOT COVER
  Exhaustiveness (that these are the ONLY families) is the enumerative
  completeness claim, not verified here; v_M sampled at {3,4,5}. The converse
  enumeration is over a finite L-window, not an a-priori proof.

CONTRACT: prints CONFIRM or FALSIFY <reason>; exit 0 / 1.
"""
import sys
from fractions import Fraction
from _reduction import obstructions, cumulative_trace, sync_level, ord2


def fail(m):
    print(f"FALSIFY {m}")
    sys.exit(1)


def run(v0, bsek, vM):
    q = 2**vM - 1
    lam = Fraction(2) ** v0
    D = Fraction(-1)
    for vK, vI in bsek:
        E = 1 - lam - q * D
        lam = lam * Fraction(2) ** (vI - vK)
        D = E / Fraction(2) ** vK
    return lam, D


def sync_form(j, vM):
    q = 2**vM - 1
    return Fraction(2) ** (j * vM), -(Fraction(2) ** (j * vM) - 1) / q


def converse_divisibility():
    """thm_recursion converse: every pre-sync lambda-exponent s is a multiple
    of v_M, for both signs of s (negative-j rational states included)."""
    total = neg = 0
    for q in (3, 7, 15):
        a = -q
        vM = ord2(a)
        for L in range(4, 16):
            for r, _ in obstructions(L, a, 1):
                k = sync_level(r, L, a, 1)
                if k is None or k < 1:
                    continue
                ct = cumulative_trace(r, L, a, 1)
                if ct is None:
                    continue
                snaps, v0 = ct
                if k - 1 >= len(snaps):
                    continue
                VK, VI = snaps[k - 1]
                s = v0 + VI - VK   # exponent of lambda_{k-1} = 2^s = 2^{j vM}
                total += 1
                if s % vM != 0:
                    fail(f"converse q={q} L={L} r={r}: pre-sync exponent s={s} "
                         f"not divisible by vM={vM} (would refute 'exactly j in Z')")
                if s < 0:
                    neg += 1
    if total == 0:
        fail("converse: vacuous, no pre-sync states enumerated")
    if neg == 0:
        fail("converse: no negative-j (rational) pre-sync states seen; "
             "the 'j in Z, not N' claim is unexercised")


def main():
    for vM in (3, 4, 5):
        # iterated node-lift families (j = 1)
        for k in range(2, 8):
            fams = [("A", vM + 1, [(vM, vM)] * (k - 2) + [(vM, vM - 1)])]
            if k >= 4:
                fams.append(("F1", vM + 1, [(vM, vM)] * (k - 4) + [(vM, vM - 2), (vM - 1, 1), (vM, 2 * vM - 1)]))
                fams.append(("B", vM - 1, [(vM - 1, 1), (vM, 2 * vM)] + [(vM, vM)] * (k - 4) + [(vM, vM - 1)]))
            if k >= 5:
                fams.append(("C", 1, [(1, vM + 1), (vM - 1, 2 * vM - 1), (2 * vM, vM)] + [(vM, vM)] * (k - 5) + [(vM, vM - 1)]))
            for name, v0, bsek in fams:
                got = run(v0, bsek, vM)
                want = sync_form(1, vM)
                if got != want:
                    fail(f"node-lift {name}_{k} vM={vM}: {got} != j=1 sync {want}")
        # universal stage-4 families
        stage4 = [
            ("A_lift", 1, vM + 1, [(vM, vM), (vM, vM), (vM, vM - 1)]),
            ("B_lift", 1, vM - 1, [(vM - 1, 1), (vM, 2 * vM), (vM, vM - 1)]),
            ("C_lift", 1, 1, [(1, vM + 1), (vM - 1, 2 * vM - 1), (2 * vM, vM - 1)]),
            ("F1", 1, vM + 1, [(vM, vM - 2), (vM - 1, 1), (vM, 2 * vM - 1)]),
            ("G1", -1, vM - 1, [(vM - 1, 1), (vM + 1, vM - 1), (2 * vM - 1, vM)]),
        ]
        for name, j, v0, bsek in stage4:
            got = run(v0, bsek, vM)
            want = sync_form(j, vM)
            if got != want:
                fail(f"stage-4 {name} vM={vM}: {got} != j={j} sync {want}")
    converse_divisibility()
    print("CONFIRM")
    sys.exit(0)


if __name__ == "__main__":
    main()
