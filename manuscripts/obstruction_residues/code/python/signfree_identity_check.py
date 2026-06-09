#!/usr/bin/env python3
"""Sign-free obstruction identity (`lem:signfree`), verified for both shift signs.

For every obstruction (every shift index s in Z), with cumulative valuations
V_K^{(j)}, V_I^{(j)} and termination index J, the identity

    sum_{j=0}^{J} 3^{J-j} 2^{V_K^{(j)}}  ==  3^{J+1} + 2^v sum_{j=0}^{J} 3^{J-j} 2^{V_I^{(j)}}

holds with no occurrence of 4^s (the two signs are treated identically).
Equivalently  hat_A_K - 2^v hat_A_I == 3^{J+1}.

This script also checks that subtracting the j=J terminal terms recovers the
positive O''-form  A_K' - 2^v A_I' == 3^{J+1} + 2^{V_I^{(J)}+v}(1-4^s)  (sums to
J-1), confirming the two are the same identity and that the s>=0 case is
reproduced verbatim. The (1-4^s) factor is kept integral as
2^{V_I^{(J)}+v} - 2^{V_K^{(J)}}.

Enumerates all obstructions up to Lmax (default 19), separates them by the sign
of s, reports any violation, and exhibits a few negative-shift instances. Pure
integer arithmetic, trajectory-based (independent of the (c,d) recursion).
Exits non-zero on any violation, or if no negative-shift obstruction is seen
(which would make the both-signs claim vacuous).
"""
import sys


def v2(n):
    return (n & -n).bit_length() - 1


def reduce_full(r, L):
    """If r in Obs_L: return (s, J, v, VK, VI) where VK, VI are the cumulative
    sequences V_K^{(j)}, V_I^{(j)} for j = 0..J (length J+1).  Else None."""
    if r & 1 == 0 or r == 1:
        return None
    v = v2(r - 1)
    if not (1 <= v < L):
        return None
    a_K, a_I = r, (r - 1) >> v
    VK, VI = [0], [0]
    while True:
        vK = v2(3 * a_K - 1)
        vI = v2(3 * a_I - 1)
        if vK >= L - VK[-1] or vI >= (L - v) - VI[-1]:
            delta = VK[-1] - VI[-1] - v
            if delta >= 0:
                X1 = (3 * a_I == (1 << delta) * (3 * a_K - 1) + 1)
            else:
                e = -delta
                X1 = ((1 << e) * 3 * a_I == (3 * a_K - 1) + (1 << e))
            if not X1 or delta % 2 != 0:
                return None
            return delta // 2, len(VK) - 1, v, VK, VI
        a_K = (3 * a_K - 1) >> vK
        a_I = (3 * a_I - 1) >> vI
        VK.append(VK[-1] + vK)
        VI.append(VI[-1] + vI)


def signfree_lhs_rhs(s, J, v, VK, VI):
    hatK = sum(3 ** (J - j) * (1 << VK[j]) for j in range(J + 1))
    hatI = sum(3 ** (J - j) * (1 << VI[j]) for j in range(J + 1))
    return hatK, 3 ** (J + 1) + (1 << v) * hatI


def o_form_lhs_rhs(s, J, v, VK, VI):
    # Positive O''-form: sums to J-1; RHS = 3^{J+1} + 2^{V_I^J+v}(1-4^s), kept
    # integral as 2^{V_I^J+v} - 2^{V_K^J} (valid for both signs).
    AKm = sum(3 ** (J - j) * (1 << VK[j]) for j in range(J))
    AIm = sum(3 ** (J - j) * (1 << VI[j]) for j in range(J))
    lhs = AKm - (1 << v) * AIm
    rhs = 3 ** (J + 1) + (1 << (VI[J] + v)) - (1 << VK[J])
    return lhs, rhs


def main():
    Lmax = int(sys.argv[1]) if len(sys.argv) > 1 else 19
    print(f"checking sign-free identity (lem:signfree) for all obstructions, L=5..{Lmax}", flush=True)
    total = {"s<0": 0, "s=0": 0, "s>0": 0}
    viol_sf = viol_o = 0
    neg_examples = []
    for L in range(5, Lmax + 1):
        for r in range(3, (1 << L) + 1, 2):
            res = reduce_full(r, L)
            if res is None:
                continue
            s, J, v, VK, VI = res
            key = "s<0" if s < 0 else ("s=0" if s == 0 else "s>0")
            total[key] += 1
            lsf, rsf = signfree_lhs_rhs(*res)
            lo, ro = o_form_lhs_rhs(*res)
            if lsf != rsf:
                viol_sf += 1
            if lo != ro:
                viol_o += 1
            if s < 0 and len(neg_examples) < 6:
                neg_examples.append((r, L, s, J, v, VK[J], VI[J]))
    print(f"obstruction counts: {total}", flush=True)
    print(f"sign-free identity  hat_A_K == 3^(J+1)+2^v hat_A_I : violations = {viol_sf}", flush=True)
    print(f"O''-form  (sums to J-1, integral)                  : violations = {viol_o}", flush=True)
    print("negative-shift instances (r, L, s, J, v, V_K^J, V_I^J):", flush=True)
    for e in neg_examples:
        print(f"   {e}", flush=True)
    ok = (viol_sf == 0 and viol_o == 0 and total["s<0"] > 0)
    print(f"\n*** sign-free identity holds for BOTH signs "
          f"(incl. {total['s<0']} negative-s obstructions): {ok} ***", flush=True)
    assert viol_sf == 0, f"sign-free identity violated in {viol_sf} cases"
    assert viol_o == 0, f"O''-form violated in {viol_o} cases"
    assert total["s<0"] > 0, (
        f"no negative-shift obstruction up to L={Lmax}, so the both-signs claim is "
        f"vacuous at this Lmax (the identity itself is not violated); rerun with a "
        f"larger Lmax -- the default Lmax=19 yields 1881 negative-shift obstructions"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
