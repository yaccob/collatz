#!/usr/bin/env python3
"""Exhaustive level-4 sub-class enumeration for thm_stage4.

WHAT THIS CHECKS
  By direct enumeration (distinguishing sub-classes by their leading
  (X_0, X_1, X_2, X_3) signature, X_j = 2^{V_K^{(j)}} - 2^{V_I^{(j)}+v}), the
  number of obstruction residues synchronising at level k = 4 falls into:
    - exactly 11 sub-classes at v_M = 3 (q = 7),
    - exactly  9 sub-classes at v_M = 4 (q = 15),
  and the five UNIVERSAL families (A_lift, B_lift, C_lift, F1, G1) are all
  present in each. Hence the q-specific count is 6 at v_M = 3 and 4 at v_M = 4
  (total minus the five universal) -- it is NOT uniform in v_M. Counts are
  L-saturated: 11 / 9 already at L = 18 and unchanged at L = 20.

WHY THIS EXISTS
  recursion.py forward-verifies that the five universal families reach their
  sync form, but does NOT enumerate the level-4 sub-classes; the q-specific
  count is asserted by the manuscript (Thm 6.1, thm:stage4) and must be guarded against
  the "four per v_M" overclaim. This check is that guard.

WHAT THIS DOES NOT COVER
  v_M >= 5 (the moduli grow as 2^{k+|j|vM}; full visibility needs larger L
  than is cheap to enumerate). The universal families are checked for presence,
  not re-derived (recursion.py does that).

CONTRACT: prints CONFIRM or FALSIFY <reason>; exit 0 / 1.
"""
import sys
from _reduction import obstructions, sync_level, cumulative_trace, ord2


def fail(m):
    print(f"FALSIFY {m}")
    sys.exit(1)


def xquad(r, L, a, c):
    snaps, v = cumulative_trace(r, L, a, c)
    return tuple((1 << vk) - (1 << (vi + v)) for vk, vi in snaps[:4])


def universal_xquads(vM):
    """Leading X-quad of each universal family from its valuation sequence."""
    fams = {
        "A_lift": (vM + 1, [(vM, vM), (vM, vM), (vM, vM - 1)]),
        "B_lift": (vM - 1, [(vM - 1, 1), (vM, 2 * vM), (vM, vM - 1)]),
        "C_lift": (1,      [(1, vM + 1), (vM - 1, 2 * vM - 1), (2 * vM, vM - 1)]),
        "F1":     (vM + 1, [(vM, vM - 2), (vM - 1, 1), (vM, 2 * vM - 1)]),
        "G1":     (vM - 1, [(vM - 1, 1), (vM + 1, vM - 1), (2 * vM - 1, vM)]),
    }
    out = {}
    for name, (v0, bsek) in fams.items():
        VK = VI = 0
        xs = [(1 << 0) - (1 << (0 + v0))]
        for vK, vI in bsek:
            VK += vK
            VI += vI
            xs.append((1 << VK) - (1 << (VI + v0)))
        out[name] = tuple(xs[:4])
    return out


# (q, L, expected total level-4 sub-class count); L-saturated.
CASES = [(7, 18, 11), (15, 18, 9)]


def main():
    for q, L, expect in CASES:
        a = -q
        vM = ord2(a)
        s4 = [r for r, _ in obstructions(L, a, 1) if sync_level(r, L, a, 1) == 4]
        sigs = {xquad(r, L, a, 1) for r in s4}
        if len(sigs) != expect:
            fail(f"q={q} (vM={vM}) L={L}: {len(sigs)} level-4 sub-classes, expected {expect}")
        uq = universal_xquads(vM)
        missing = [name for name, xq in uq.items() if xq not in sigs]
        if missing:
            fail(f"q={q} (vM={vM}): universal families absent from enumeration: {missing}")
        # q-specific = total - 5 universal; report the non-uniformity guard
        qspec = len(sigs) - len(uq)
        want_qspec = {3: 6, 4: 4}[vM]
        if qspec != want_qspec:
            fail(f"q={q} (vM={vM}): {qspec} q-specific level-4 families, expected {want_qspec}")
    print("CONFIRM")
    sys.exit(0)


if __name__ == "__main__":
    main()
