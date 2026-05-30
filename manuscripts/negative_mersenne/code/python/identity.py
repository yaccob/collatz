#!/usr/bin/env python3
"""Checks for thm_main_identity, cor_mersenne_sync, cor_nonmersenne.

WHAT THIS CHECKS (exact integer arithmetic over many samples)
  Main identity (q = 2^vM - 1 Mersenne), for r + c = 2^v m:
      -q r + c == 2^v (-q m + c) + (2^vM - 2^v) c.
  Mersenne sync (cor 1.1): at v = vM the correction (2^vM - 2^v) c is 0.
  Universal form + non-Mersenne (cor 1.2): for ANY q,
      -q r + c == 2^v (-q m + c) + (q + 1 - 2^v) c,
  and for non-Mersenne q (q+1 not a power of two) the correction
  (q + 1 - 2^v) c is never 0 for odd c — so no clean main-class sync.

WHAT THIS DOES NOT COVER
  These are polynomial identities; the sampled check falsifies a wrong
  stated identity (sign/term error), it is not a symbolic proof.

CONTRACT: prints CONFIRM or FALSIFY <reason>; exit 0 / 1.
"""
import sys


def fail(m):
    print(f"FALSIFY {m}")
    sys.exit(1)


def main():
    odd_c = (-5, -3, -1, 1, 3, 5)
    # Mersenne main identity + Mersenne-sync corollary
    for vM in range(2, 9):
        q = 2**vM - 1
        for v in range(1, 9):
            for m in range(-6, 7):
                for c in odd_c:
                    r = (1 << v) * m - c
                    lhs = -q * r + c
                    rhs = (1 << v) * (-q * m + c) + ((1 << vM) - (1 << v)) * c
                    if lhs != rhs:
                        fail(f"main identity vM={vM} v={v} m={m} c={c}: {lhs} != {rhs}")
            if ((1 << vM) - (1 << vM)) * 1 != 0:  # v == vM correction vanishes
                fail(f"mersenne-sync: correction at v=vM nonzero (vM={vM})")

    # Universal identity (any q) + non-Mersenne asymmetry
    for q in range(2, 48):
        is_mersenne = ((q + 1) & q) == 0          # q+1 a power of two
        for v in range(1, 9):
            for m in range(-4, 5):
                for c in odd_c:
                    r = (1 << v) * m - c
                    lhs = -q * r + c
                    rhs = (1 << v) * (-q * m + c) + (q + 1 - (1 << v)) * c
                    if lhs != rhs:
                        fail(f"universal identity q={q} v={v} m={m} c={c}")
        if not is_mersenne:
            for v in range(1, 12):
                for c in odd_c:
                    if (q + 1 - (1 << v)) * c == 0:
                        fail(f"non-Mersenne correction == 0 at q={q} v={v} c={c}")
    print("CONFIRM")
    sys.exit(0)


if __name__ == "__main__":
    main()
