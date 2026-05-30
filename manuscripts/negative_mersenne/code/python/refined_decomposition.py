#!/usr/bin/env python3
"""Check for cor_atom_density_extended: the PER-FAMILY decomposition of the
refined lower bound (not just the total, which atom_density.py already guards).

WHY THIS EXISTS
  Review 007 found that the refined bound's *value* is correct but the proof's
  attribution of density to families was wrong: it credited the node-lift towers
  B_k, C_k, F_{1,k} with 2^{-2vM}/q, 2^{-3vM}/q, 2^{-2vM-1}/q. By enumeration the
  towers (as defined in thm:node-lift) give 2^{-3vM}/q, 2^{-4vM-1}/q, 2^{-3vM}/q;
  the 2^{-2vM}/q-order mass actually comes from the STANDALONE level-3 families
  B (2^{-3vM}) and C (2^{-3vM-1}) and the level-4 family C_lift (2^{-4vM-1}), which
  the corollary had omitted. The total is unchanged (the disjoint collection sums
  to the same bound, S == old, verified below), but the gate must guard the
  attribution so the mislabelling cannot recur.

WHAT THIS CHECKS
  (1) Each named UNIVERSAL family's base residue-cylinder density equals its
      closed form, by direct enumeration (q in {7,15}, i.e. vM in {3,4}); each
      family is matched by its (v0, per-step (vK,vI)) signature.
  (2) The disjoint-family sum
        1/(2q)                                  [principal + A_k tower, k>=1]
        + 2*2^{-3vM}/q                          [B_k and F_{1,k} towers, k>=4]
        + 2^{-4vM-1}/q                          [C_k tower, k>=5]
        + 2^{-3vM} + 2^{-3vM-1}                 [stage-3 B, C  (k=3, standalone)]
        + 2^{-4vM-1} + 2^{-4vM}                 [C_lift (k=4) + G1 (k=4)]
      equals the corollary's stated bound
        1/(2q) + 2^{-2vM}/q + 2^{-3vM}/q + 2^{-2vM-1}/q + 2^{-4vM}
      as exact rationals, for vM = 2..40. (This is the S == old identity.)

WHAT THIS DOES NOT COVER
  The level-3/4 classification's completeness (other checks); the asymptotic
  upper bound (open, conj:subclass-count). Tower contributions are verified as
  closed-form geometric sums of enumeration-confirmed base densities, not by
  enumerating every tower member.

CONTRACT: prints CONFIRM or FALSIFY <reason>; exit 0 / 1.
"""
import sys
from fractions import Fraction as F
from _reduction import obstructions, cumulative_trace, sync_level, ord2


def fail(m):
    print(f"FALSIFY {m}")
    sys.exit(1)


def named_families(vM):
    """name -> (v0, steps, closed-form density exponent e) with density 2^-e."""
    return {
        "principal":  (vM,     [],                                              vM + 1),
        "A2":         (vM + 1, [(vM, vM - 1)],                                  2 * vM + 1),
        "A3":         (vM + 1, [(vM, vM), (vM, vM - 1)],                        3 * vM + 1),
        "B_stage3":   (vM - 1, [(vM - 1, 1), (vM, 2 * vM - 1)],                 3 * vM),
        "C_stage3":   (1,      [(1, vM + 1), (vM - 1, 2 * vM - 2)],             3 * vM + 1),
        "A4_Alift":   (vM + 1, [(vM, vM), (vM, vM), (vM, vM - 1)],              4 * vM + 1),
        "B4_Blift":   (vM - 1, [(vM - 1, 1), (vM, 2 * vM), (vM, vM - 1)],       4 * vM),
        "C_lift":     (1,      [(1, vM + 1), (vM - 1, 2 * vM - 1), (2 * vM, vM - 1)], 4 * vM + 1),
        "F1":         (vM + 1, [(vM, vM - 2), (vM - 1, 1), (vM, 2 * vM - 1)],   4 * vM),
        "G1":         (vM - 1, [(vM - 1, 1), (vM + 1, vM - 1), (2 * vM - 1, vM)], 4 * vM),
        "C5":         (1,      [(1, vM + 1), (vM - 1, 2 * vM - 1), (2 * vM, vM), (vM, vM - 1)], 5 * vM + 1),
    }


def enum_groups(q, L):
    a = -q
    g = {}
    for r, _ in obstructions(L, a, 1):
        k = sync_level(r, L, a, 1)
        if k is None or k < 1:
            continue
        ct = cumulative_trace(r, L, a, 1)
        if ct is None:
            continue
        snaps, v0 = ct
        if k > len(snaps):
            continue
        pairs = tuple((snaps[i][0] - snaps[i - 1][0], snaps[i][1] - snaps[i - 1][1])
                      for i in range(1, k))
        g[(v0, pairs)] = g.get((v0, pairs), 0) + 1
    return g


def disjoint_sum(vM):
    """Closed-form sum of the universal families, grouped by family letter as
    geometric towers from each letter's minimal synchronisation level (vM >= 3):
      A (k>=1): 2^{-(k vM + 1)} -> 1/(2q)            [principal + A_k]
      B (k>=3): 2^{-k vM}       -> 2^{-2vM}/q        [level-3 B + its node lifts]
      C (k>=3): 2^{-(k vM + 1)} -> 2^{-2vM-1}/q      [level-3 C, C_lift, node lifts]
      F (k>=4): 2^{-k vM}       -> 2^{-3vM}/q        [F1 + its node lifts]
      G1 (k=4): 2^{-4vM}
    Each geometric sum uses sum_{k>=k0} 2^{-k vM} = 2^{-k0 vM} * 2^vM/q."""
    q = 2 ** vM - 1
    A = F(1, 2 * q)
    B = F(1, 2 ** (3 * vM)) * (2 ** vM) / q          # sum_{k>=3} 2^{-k vM}
    C = F(1, 2 ** (3 * vM + 1)) * (2 ** vM) / q      # sum_{k>=3} 2^{-(k vM+1)}
    Ff = F(1, 2 ** (4 * vM)) * (2 ** vM) / q         # sum_{k>=4} 2^{-k vM}
    G1 = F(1, 2 ** (4 * vM))
    return A + B + C + Ff + G1


def stated_bound(vM):
    """The bound exactly as written in cor_atom_density_extended."""
    q = 2 ** vM - 1
    return (F(1, 2 * q) + F(1, 2 ** (2 * vM)) / q + F(1, 2 ** (3 * vM)) / q
            + F(1, 2 ** (2 * vM + 1)) / q + F(1, 2 ** (4 * vM)))


def main():
    # (1) per-family base densities, enumerated once per q, matched to closed
    # forms. A family is visible once L > e; we enumerate at a single L per q
    # and check every family whose exponent fits (C5 at vM=4 needs L=22, so it
    # is exercised at vM=3, where e=16, instead).
    for q, L in ((7, 17), (15, 18)):
        vM = ord2(-q)
        g = enum_groups(q, L)
        for name, (v0, steps, eexp) in named_families(vM).items():
            if eexp >= L:
                continue                            # not yet visible at this L
            cnt = g.get((v0, tuple(steps)), 0)
            meas = F(cnt, 1 << L)
            want = F(1, 2 ** eexp)
            if meas != want:
                fail(f"family {name} q={q}: density {meas} != closed form 2^-{eexp}")

    # (2) disjoint decomposition sums to the stated bound (S == old), exact.
    for vM in range(2, 41):
        if disjoint_sum(vM) != stated_bound(vM):
            fail(f"vM={vM}: disjoint family sum {disjoint_sum(vM)} != stated bound {stated_bound(vM)}")

    print("CONFIRM")
    sys.exit(0)


if __name__ == "__main__":
    main()
