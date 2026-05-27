"""Verify that the multiplicative bijection r -> c*r mod 2^L holds for L up to 16,
and check whether shift indices are preserved (i.e., a^{(c)}(c*r mod 2^L) = a^{(1)}(r, L)).
"""

from alternative_setups import parallel_reduce_variantB, is_obstr_B


def enumerate_with_shift(L, c):
    out = {}
    for r in range(1, 1 << L, 2):
        ep = parallel_reduce_variantB(r, L, c)
        if is_obstr_B(ep, c):
            coef, dval, V_K, V_I, v = ep
            delta = V_K - V_I - v
            out[r] = (delta, coef, dval)
    return out


def main():
    print("# Verification: r -> c*r mod 2^L is a shift-preserving bijection Obs^{(1)} -> Obs^{(c)}")
    print()
    L = 12
    obs_1 = enumerate_with_shift(L, 1)
    print(f"At L={L}: |Obs^{{(1)}}| = {len(obs_1)}")
    print()
    for c in [-7, -5, -3, -1, 3, 5, 7, 9, 11, 13]:
        obs_c = enumerate_with_shift(L, c)
        mod = 1 << L
        # Apply r -> c*r mod 2^L and check shift indices
        mismatches = 0
        bij_size = 0
        for r, (delta1, _, _) in obs_1.items():
            r_image = (c * r) % mod
            if r_image in obs_c:
                bij_size += 1
                delta_c = obs_c[r_image][0]
                if delta_c != delta1:
                    mismatches += 1
        cover = len(obs_c) == bij_size and len(obs_1) == bij_size
        print(f"c={c:+d}: |Obs|={len(obs_c)}, bijection covers all: {cover}, shift mismatches: {mismatches}")


if __name__ == "__main__":
    main()
