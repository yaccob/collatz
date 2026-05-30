#!/usr/bin/env python3
"""Check for thm_stage3_structure.

WHAT THIS CHECKS
  (1) Stage-3 obstructions (sync stage k = 3) fall into exactly the stated
      number of universal sub-classes: 3 for v_M >= 3, and 4 for v_M = 2 (the
      extra D_hyper family). Sub-classes are distinguished by their leading
      (X_0, X_1, X_2) triple. Verified by direct enumeration for q in {3 (vM=2),
      7 (vM=3), 15 (vM=4)}.
  (2) The explicit substitution-chain constants of Thm 5.1: family A residues
      satisfy r = 2^{3vM} nu - K_A c with K_A = 2^{2vM+2} + 2^{vM+1} + 1 and nu
      odd (v_0 = vM+1); family B residues r = 2^{3vM} tau - K_B c with
      K_B = 5*2^{2vM-1} + 3*2^{vM-1} + 1 (v_0 = vM-1). Checked for q in {7, 15}.
  (3) The illustrative stage-3 counts in the proof: 132 obstruction residues at
      L=12 for q=3, 64 at L=14 for q=7 (these are obstruction residues, NOT
      atoms -- the atom count at these levels is 0).

WHAT THIS DOES NOT COVER
  Universality of K_A, K_B over all v_M (only q in {7,15} sampled); the
  general-v_M exhaustiveness of the family classification.

CONTRACT: prints CONFIRM or FALSIFY <reason>; exit 0 / 1.
"""
import sys
from _reduction import obstructions, sync_level, cumulative_trace, ord2


def fail(m):
    print(f"FALSIFY {m}")
    sys.exit(1)


def _xs3(r, L, a, c):
    snaps, v = cumulative_trace(r, L, a, c)
    return tuple((1 << vk) - (1 << (vi + v)) for vk, vi in snaps[:3])


def _v2(n):
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c


def main():
    # (1) sub-class count per instance.
    for q, L in [(3, 14), (7, 14), (15, 16)]:
        a = -q
        vM = ord2(a)
        fams = {_xs3(r, L, a, 1) for r, _ in obstructions(L, a, 1)
                if sync_level(r, L, a, 1) == 3}
        expect = 4 if vM == 2 else 3
        if len(fams) != expect:
            fail(f"q={q} (vM={vM}): {len(fams)} stage-3 sub-classes, expected {expect}")

    # (2) substitution-chain constants K_A, K_B (Thm 5.1).
    for q, L in [(7, 14), (15, 16)]:
        a = -q
        vM = ord2(a)
        c = 1
        KA = 2 ** (2 * vM + 2) + 2 ** (vM + 1) + 1
        KB = 5 * 2 ** (2 * vM - 1) + 3 * 2 ** (vM - 1) + 1
        mod = 2 ** (3 * vM)
        s3 = [r for r, _ in obstructions(L, a, c) if sync_level(r, L, a, c) == 3]
        A = [r for r in s3 if _v2(r + c) == vM + 1]
        B = [r for r in s3 if _v2(r + c) == vM - 1]
        for r in A:
            if (r + KA * c) % mod != 0:
                fail(f"K_A q={q}: r={r} not == 2^3vM*nu - K_A*c (K_A={KA})")
            if ((r + KA * c) // mod) % 2 == 0:
                fail(f"K_A q={q}: nu even for r={r}")
        for r in B:
            if (r + KB * c) % mod != 0:
                fail(f"K_B q={q}: r={r} not == 2^3vM*tau - K_B*c (K_B={KB})")

    # (3) illustrative stage-3 obstruction-residue counts (proof of Thm 5.1).
    for q, L, want in [(3, 12, 132), (7, 14, 64)]:
        a = -q
        n = sum(1 for r, _ in obstructions(L, a, 1) if sync_level(r, L, a, 1) == 3)
        if n != want:
            fail(f"stage-3 count q={q} L={L}: {n} obstruction residues, expected {want}")

    print("CONFIRM")
    sys.exit(0)


if __name__ == "__main__":
    main()
