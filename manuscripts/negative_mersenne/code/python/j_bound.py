#!/usr/bin/env python3
"""Check for thm_j_bound (j-observability bound).

WHAT THIS CHECKS
  For every atomic obstruction at level L (q in {3,7,15} Mersenne), with
  sync stage k and signed sync parameter j, the visibility bound
      |j| <= (L - k) / v_M,   i.e.   |j| * v_M <= L - k
  holds. (k = sync_level, j = delta_J / v_M = shift_index for a = -q since
  ord_q(2) = v_M.) Counted by direct enumeration; any violation falsifies.

WHAT THIS DOES NOT COVER
  Finite-L window; it falsifies a counterexample if one exists in range,
  it does not re-derive the modulus argument.

CONTRACT: prints CONFIRM or FALSIFY <reason>; exit 0 / 1.
"""
import sys
from _reduction import obstructions, sync_level, shift_index, is_atomic, ord2


def fail(m):
    print(f"FALSIFY {m}")
    sys.exit(1)


def main():
    tested = 0
    for q in (3, 7, 15):
        a = -q
        vM = ord2(a)
        for L in range(4, 15):
            for r, ep in obstructions(L, a, 1):
                if not is_atomic(r, L, a, 1):
                    continue
                k = sync_level(r, L, a, 1)
                j = shift_index(ep, a)
                if k is None or j is None:
                    continue
                tested += 1
                if abs(j) * vM > L - k:
                    fail(f"q={q} L={L} r={r}: |j|={abs(j)} k={k} -> |j|*vM={abs(j)*vM} > L-k={L-k}")
    if tested == 0:
        fail("vacuous: no atoms enumerated")
    print("CONFIRM")
    sys.exit(0)


if __name__ == "__main__":
    main()
