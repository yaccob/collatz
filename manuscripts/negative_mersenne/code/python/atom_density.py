#!/usr/bin/env python3
"""Checks for thm_atom_density_lower and cor_atom_density_extended.

WHAT THIS CHECKS
  (1) The density lower bound c_W^{(-q)} >= 1/(2q): every finite quotient
      |O_L^{(-q,1)}|/2^L is itself a rigorous lower bound on the limit c_W, so
      it must already exceed 1/(2q). Verified by direct enumeration for
      q in {3, 7, 15} (Mersenne) at several L.
  (2) The values printed in the manuscript's density table (Sec. 8): for each
      vM in {2,3,4,5} it recomputes the simple bound 1/(2q), the refined bound
      of the corollary (exact rational arithmetic), and the finite density
      |O_L^{(-q,1)}|/2^L at the level L the table reports, and checks each
      against the tabulated value (to the displayed 4-decimal precision). This
      guards the table against transcription / staleness errors.

WHAT THIS DOES NOT COVER
  The refined bound (cor) is a lower bound on the LIMIT c_W; finite densities
  approach c_W from below and can sit just under the refined bound for large
  vM (the table shows them agreeing to 4 decimals for vM >= 4). So this checks
  that the tabulated finite density is reproduced, NOT that finite >= refined.
  The asymptotic tightness (thm_asymptotik_cW) is out of scope (waived there).

CONTRACT: prints CONFIRM or FALSIFY <reason>; exit 0 / 1.
"""
import sys
from fractions import Fraction
from _reduction import obstructions


def fail(m):
    print(f"FALSIFY {m}")
    sys.exit(1)


def refined_bound(vM):
    """cor_atom_density_extended: 1/(2q) + 2^-2vM/q + 2^-3vM/q + 2^-2vM-1/q + 2^-4vM."""
    q = 2**vM - 1
    return (Fraction(1, 2 * q)
            + Fraction(1, 2**(2 * vM)) / q
            + Fraction(1, 2**(3 * vM)) / q
            + Fraction(1, 2**(2 * vM + 1)) / q
            + Fraction(1, 2**(4 * vM)))


# Manuscript Sec. 8 table, 4-decimal display; finite density at L = 16.
# columns: vM -> (1/(2q), refined bound, |O_L|/2^L at L=16)
TABLE_L = 16
TABLE = {
    2: (0.1667, 0.2070, 0.2498),
    3: (0.0714, 0.0753, 0.0770),
    4: (0.0333, 0.0338, 0.0338),
    5: (0.0161, 0.0162, 0.0162),
}
TOL = 5e-5  # matches a 4-decimal rounded display


def main():
    # (1) the comfortable lower bound, several L
    for q in (3, 7, 15):
        a = -q
        for L in (12, 14, 16):
            n = len(obstructions(L, a, 1))
            dens = Fraction(n, 1 << L)
            if dens < Fraction(1, 2 * q):
                fail(f"q={q} L={L}: density {float(dens):.5f} < 1/(2q) = {1/(2*q):.5f}")

    # (2) the manuscript density table
    for vM, (simple_t, refined_t, dens_t) in TABLE.items():
        q = 2**vM - 1
        simple = float(Fraction(1, 2 * q))
        refined = float(refined_bound(vM))
        dens = float(Fraction(len(obstructions(TABLE_L, -q, 1)), 1 << TABLE_L))
        if abs(simple - simple_t) > TOL:
            fail(f"table 1/(2q) vM={vM}: {simple:.5f} != tabulated {simple_t}")
        if abs(refined - refined_t) > TOL:
            fail(f"table refined vM={vM}: {refined:.5f} != tabulated {refined_t}")
        if abs(dens - dens_t) > TOL:
            fail(f"table density vM={vM} L={TABLE_L}: {dens:.5f} != tabulated {dens_t}")

    print("CONFIRM")
    sys.exit(0)


if __name__ == "__main__":
    main()
