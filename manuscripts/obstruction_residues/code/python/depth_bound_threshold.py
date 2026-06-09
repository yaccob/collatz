#!/usr/bin/env python3
"""Large-shift depth bound J >= 2|s|+3 for |s| >= 4 (`lem:depth-negbig`).

From the sign-free identity (`lem:signfree`, signfree_identity_check.py) plus two
elementary bounds, a negative-shift obstruction with |s| = a satisfies

  (lower)  hat_A_K  >  2^v hat_A_I  >=  2^{V_K^J + 2a}     (top I-term; V_I^J+v = V_K^J+2a)
  (upper)  hat_A_K  =  sum_j 3^{J-j} 2^{V_K^j}
                    <= 2^{V_K^J} sum_{i=0}^{J} (3/2)^i      (since V_K^j <= V_K^J-(J-j))
                    <  2^{V_K^J} * 3^{J+1} / 2^J.

Cancelling 2^{V_K^J}:   3^{J+1} > 2^{J+2a}    ... (N)   [necessary for an obstruction]

f(J) := 3^{J+1}/2^{J+2a} is strictly increasing in J, so (N) fails for every
J <= J*, where J* is the largest J with 3^{J+1} <= 2^{J+2a}; hence every such
obstruction has J >= J*+1. This script computes J*+1 per a and compares it to the
target 2a+3, exhibiting:
  - a >= 4 : J*+1 >= 2a+3  -> the bound is PROVEN by (N) alone;
  - a = 2,3: J*+1 <  2a+3  -> (N) is insufficient (the finite tails, closed by
             depth_carry_automaton_neg.py).
The threshold is exact:  f(2a+2) = (27/4)(9/16)^a < 1  iff  a >= 4.

Exits non-zero if (N) fails to force 2a+3 for any a >= 4, or if the
(27/4)(9/16)^a < 1 threshold does not coincide with a >= 4.
"""
import sys
from fractions import Fraction


def largest_J_ruled_out(a):
    """Largest J with 3^{J+1} <= 2^{J+2a} (i.e. the necessary condition (N) fails)."""
    J, last = 0, -1
    while 3 ** (J + 1) <= 2 ** (J + 2 * a):
        last = J
        J += 1
        if J > 10 * a + 50:   # safety; f(J) is increasing past the crossover
            break
    return last


def main():
    print(" a  target 2a+3  J*+1 (forced by (N))  f(2a+2)=(27/4)(9/16)^a   verdict", flush=True)
    ok_bound = True
    threshold_consistent = True
    for a in range(2, 13):
        J_forced = largest_J_ruled_out(a) + 1
        target = 2 * a + 3
        f = Fraction(27, 4) * Fraction(9, 16) ** a   # = 3^{2a+3}/2^{4a+2}
        forced_ok = J_forced >= target
        verdict = "PROVEN by (N)" if forced_ok else "(N) insufficient -> tail"
        print(f"{a:<3} {target:<12} {J_forced:<20} {float(f):<23.5f} {verdict}  (f<1: {f < 1})", flush=True)
        if a >= 4 and not forced_ok:
            ok_bound = False
        # threshold must coincide exactly with a >= 4
        if (f < 1) != (a >= 4):
            threshold_consistent = False
    print("\nThreshold: f(2a+2) < 1  <=>  a >= 4  (f = (27/4)(9/16)^a is decreasing in a).", flush=True)
    print("=> J >= 2|s|+3 is PROVEN by (N) for |s| >= 4; |s| = 2,3 are the finite tails.", flush=True)
    assert ok_bound, "(N) failed to force J >= 2a+3 for some a >= 4"
    assert threshold_consistent, "(27/4)(9/16)^a < 1 does not coincide with a >= 4"
    sys.exit(0)


if __name__ == "__main__":
    main()
