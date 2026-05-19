"""Quick enumeration of all obstructions and their shift indices at a given L."""
import sys
from fractions import Fraction

def v2(n):
    if n == 0:
        return 10**9
    n = abs(n)
    c = 0
    while (n & 1) == 0:
        n >>= 1
        c += 1
    return c

def parallel_reduce(r, L):
    if r % 2 == 0 or r % 4 != 3:
        return None
    v = v2(r - 1)
    if v <= 0 or v >= L:
        return None
    
    factor = 1 << v
    m = (r - 1) // factor
    a_K, b_K = r, 1 << L
    a_I, b_I = m, 1 << (L - v)
    c = Fraction(1, factor)
    d = Fraction(-1, factor)
    
    while True:
        three_aK = 3 * a_K - 1
        v_K = v2(three_aK)
        v_b_K = v2(b_K)
        three_aI = 3 * a_I - 1
        v_I = v2(three_aI)
        v_b_I = v2(b_I)
        
        if v_K >= v_b_K or v_I >= v_b_I:
            return (c, d)
        
        c_old = c
        c = c_old * Fraction(1 << v_K, 1 << v_I)
        d = (3 * d + c_old - 1) / Fraction(1 << v_I)
        a_K = three_aK >> v_K
        b_K = (3 * b_K) >> v_K
        a_I = three_aI >> v_I
        b_I = (3 * b_I) >> v_I

def shift_index_from_endpoint(c, d):
    """Extract shift index a from (c,d) endpoint where c = 4^a, d = (1-4^a)/3."""
    X = 3 * d + c
    if X != 1:
        return None
    if c <= 0:
        return None
    if c.denominator == 1:
        c_int = c.numerator
        if c_int == 0:
            return None
        a = 0
        c_test = 1
        while c_test < c_int:
            c_test *= 4
            a += 1
        if c_test != c_int:
            return None
        expected_d = Fraction(1 - c_int, 3)
        if d != expected_d:
            return None
        return a
    if c.numerator == 1:
        denom = c.denominator
        a = 0
        d_test = 1
        while d_test < denom:
            d_test *= 4
            a += 1
        if d_test != denom:
            return None
        expected_d = (1 - c) / 3
        if d != expected_d:
            return None
        return -a
    return None

def is_atomic(r, L):
    """Check if r is atomic at level L."""
    if L == 6:
        return True
    result = parallel_reduce(r % (1 << (L-1)), L - 1)
    return result is None

L = int(sys.argv[1]) if len(sys.argv) > 1 else 8

obstructions = []
for r in range(1, 1 << L, 2):
    endpoint = parallel_reduce(r, L)
    if endpoint is not None and 3 * endpoint[1] + endpoint[0] == 1:
        a = shift_index_from_endpoint(endpoint[0], endpoint[1])
        obstructions.append((r, a))

print(f"L={L}")
print(f"|Obs_L| = {len(obstructions)}")

g_0_count = sum(1 for _, a in obstructions if a == 0)
g_ne0_count = sum(1 for _, a in obstructions if a != 0)
print(f"|Obs_L^{{G_0}}| = {g_0_count}")
print(f"|Obs_L^{{G_{{ne0}}}}| = {g_ne0_count}")

atoms = [(r, a) for r, a in obstructions if is_atomic(r, L)]
atoms_ne0 = sum(1 for _, a in atoms if a != 0)
print(f"|Atom_L^{{G_{{ne0}}}}| = {atoms_ne0}")
