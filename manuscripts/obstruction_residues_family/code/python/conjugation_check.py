"""For variant B (m := (r + c)/2^v), the counts |Obs_L^{(c)}| are identical
across all odd c.  This is a strong claim suggesting a *universal* family
that does not depend on the constant c at all.

Hypothesis: there exists a bijection r -> psi_c(r) from Obs_L^{(1)} to Obs_L^{(c)}
that is *not* the identity (the residues differ between c=1 and c=5 above),
but possibly a multiplicative one.

Test:
1. List Obs_L^{(1)} and Obs_L^{(5)} for small L.
2. Check whether multiplication by 5 mod 2^L is the bijection.
3. Verify parity lemma (delta even) for all c.
4. Verify shift-index distribution matches.
"""

from alternative_setups import parallel_reduce_variantB, is_obstr_B, v2
from fractions import Fraction


def enumerate_B(L, c):
    obstr = []
    for r in range(1, 1 << L, 2):
        ep = parallel_reduce_variantB(r, L, c)
        if is_obstr_B(ep, c):
            coef, dval, V_K, V_I, v = ep
            delta = V_K - V_I - v
            obstr.append((r, delta, coef, dval))
    return obstr


def main():
    print("# Verify identical counts and parity-lemma compliance for variant B")
    print()
    print("c | L=6 | L=8 | L=10 | L=12 | parity-violations")
    print("---|---|---|---|---|---")
    for c in [-13, -11, -9, -7, -5, -3, -1, 1, 3, 5, 7, 9, 11, 13]:
        counts = []
        violations = 0
        for L in [6, 8, 10, 12]:
            obstr = enumerate_B(L, c)
            counts.append(len(obstr))
            if L == 12:
                violations = sum(1 for _, delta, *_ in obstr if delta % 2 != 0)
        print(f"{c:+d} | " + " | ".join(str(x) for x in counts) + f" | {violations}")

    print()
    print("# Multiplicative bijection conjecture: Obs_L^{(c)} = c * Obs_L^{(1)} mod 2^L?")
    print()
    L = 8
    obs_1 = enumerate_B(L, 1)
    set_1 = set(r for r, *_ in obs_1)
    for c in [-7, -5, -3, -1, 1, 3, 5, 7]:
        obs_c = enumerate_B(L, c)
        set_c = set(r for r, *_ in obs_c)
        # Compute c * Obs_1 mod 2^L (only sensible for gcd(c, 2)=1)
        mod = 1 << L
        c_inv = pow(c % mod, -1, mod) if c % 2 == 1 else None
        # Test 1: set_c == {c * r mod 2^L : r in set_1}
        test1 = set((c * r) % mod for r in set_1)
        match1 = test1 == set_c
        # Test 2: set_c == {c^{-1} * r mod 2^L : r in set_1}
        test2 = set((c_inv * r) % mod for r in set_1) if c_inv else None
        match2 = (test2 == set_c) if c_inv else False
        print(f"c={c:+d}: |Obs|={len(set_c)}, c*Obs_1 mod 2^L matches? {match1}; c^-1*Obs_1 matches? {match2}")
        if not match1 and not match2:
            sample_c = sorted(set_c)[:5]
            sample_1 = sorted(set_1)[:5]
            print(f"   sample Obs_{c}: {sample_c}")
            print(f"   sample Obs_1: {sample_1}")

    print()
    print("# Detailed Obs_8 for several c:")
    print()
    for c in [-3, -1, 1, 3, 5, 7]:
        obs = enumerate_B(8, c)
        print(f"c={c:+d}: {[r for r, *_ in obs]}")


if __name__ == "__main__":
    main()
