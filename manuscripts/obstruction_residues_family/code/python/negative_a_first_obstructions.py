"""First step of the negative-a investigation: verify Conjecture 1 and
determine the residual characterisation of the obstructions O_L^(-1, c).

Conjecture 1 (degenerate case a = -1):
    |O_L^(-1, c)| = 2^(L-2)   for every odd c and every L >= 3.

Here we verify this for c in {-5, -3, -1, +1, +3, +5} up to L = 14 and also
list the concrete residues to reveal the structure.
"""

import sys
from count_obstructions_ac import enumerate_obstructions


def verify_conjecture_1(L_max: int = 14):
    """Table |Obs| vs. 2^{L-2} for several c-values."""
    cs = [-5, -3, -1, 1, 3, 5]
    print(f"# Conjecture 1: |O_L^(-1, c)| = 2^(L-2), tested up to L={L_max}")
    print()
    header = ["L", "2^(L-2)"] + [f"c={c:+d}" for c in cs]
    print(" | ".join(header))
    print(" | ".join(["---"] * len(header)))
    all_match = True
    for L in range(3, L_max + 1):
        expected = 1 << (L - 2)
        row = [str(L), str(expected)]
        for c in cs:
            obs = enumerate_obstructions(L, -1, c)
            count = len(obs)
            mark = "" if count == expected else "  MISMATCH"
            row.append(f"{count}{mark}")
            if count != expected:
                all_match = False
        print(" | ".join(row))
    print()
    print(f"All values match: {all_match}")
    return all_match


def residual_classes(L_max: int = 10, c: int = 1):
    """List all obstructions as residues mod 2^L and check whether there is a
    residue-class structure mod 2^k for small k."""
    print()
    print(f"# Residual structure of O_L^(-1, c={c:+d}), L = 3 .. {L_max}")
    print()
    for L in range(3, L_max + 1):
        obs = enumerate_obstructions(L, -1, c)
        rs = sorted(r for r, _, _ in obs)
        print(f"L={L}: |Obs|={len(rs)}, residues mod 2^{L}: {rs}")


def constancy_mod_4_check(L_max: int = 12, c: int = 1):
    """A specific structural hypothesis: every obstruction has a fixed
    residue mod 4 or mod 8 etc."""
    print()
    print(f"# Distribution of obstruction residues mod 4, 8, 16 (c={c:+d})")
    print()
    for L in range(3, L_max + 1):
        obs = enumerate_obstructions(L, -1, c)
        rs = sorted(r for r, _, _ in obs)
        d4 = {r % 4 for r in rs}
        d8 = {r % 8 for r in rs}
        d16 = {r % 16 for r in rs}
        print(f"L={L:2d}: |Obs|={len(rs):5d}, mod 4: {sorted(d4)}, mod 8: {sorted(d8)}, mod 16: {sorted(d16)[:10]}")


def lift_balance_check(L_max: int = 12, c: int = 1):
    """Check whether the obstruction set doubles perfectly under the lift
    r -> r or r -> r + 2^L (strict lift balance, no atomic contribution)."""
    print()
    print(f"# Lift balance: is each r in O_L lifted (one of r, r+2^L) into an obstruction in O_{{L+1}}? (c={c:+d})")
    print()
    for L in range(3, L_max):
        obs_L = {r for r, _, _ in enumerate_obstructions(L, -1, c)}
        obs_L1 = {r for r, _, _ in enumerate_obstructions(L + 1, -1, c)}
        # Lifts of r in obs_L are r, r + 2^L
        lifts = set()
        for r in obs_L:
            lifts.add(r)
            lifts.add(r + (1 << L))
        # Strict lift balance: lifts contain obs_L1 and |obs_L1| = 2 * |obs_L|
        ratio = len(obs_L1) / max(len(obs_L), 1)
        included = obs_L1 <= lifts
        atoms = obs_L1 - lifts
        print(
            f"L={L:2d}: |O_L|={len(obs_L):4d}, |O_{{L+1}}|={len(obs_L1):4d}, "
            f"ratio={ratio:.3f}, lifts contain O_{{L+1}}: {included}, "
            f"atoms (in O_{{L+1}} but not lifted): {len(atoms)}"
        )


def main():
    L_max = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    verify_conjecture_1(L_max)
    residual_classes(min(L_max, 10), c=1)
    constancy_mod_4_check(L_max, c=1)
    lift_balance_check(L_max, c=1)
    print()
    print("# Extra: c=-1")
    residual_classes(min(L_max, 10), c=-1)
    print()
    print("# Extra: c=+3")
    residual_classes(min(L_max, 10), c=3)


if __name__ == "__main__":
    main()
