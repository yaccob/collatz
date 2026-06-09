#!/usr/bin/env python3
"""Positive q-bounded residual tails closed by exhaustive coupled DFS.

After the closed-form bound (`lem:depth-posbig`, depth_closed_form.py) the
positive small-shift strata reduce to finitely many residual cells, listed by
depth_closed_form.py part 4:

  * s=3:  closed form covers J <= 7 entirely and J=8 for q >= 1 and (q=0, v=1);
          residual = (J=8, q=0, v in [2,8])              -- 7 cells.
  * s=2:  closed form covers J <= 4 entirely and J=5 for q >= 2;
          residual = (J=5, q in {0,1}, v in [1,5])        -- 9 cells.
          (the remaining s=2 stratum J=6 is q-unbounded -> carry automaton,
          depth_carry_automaton_k2.py, not here.)

This script settles those residual cells directly by exhaustive DFS over the true
reduction sequences (respecting the full (V_K,V_I) coupling). The DFS enumerates
all (v_K, v_I) step-valuation sequences compatible with the proved structural
constraints (K-track prefix `lem:k-prefix`: v_K^(0)>=2 if v=1, else v_K^(j)=1 for
j<=v-2 and v_K^(v-1)>=2; cumulative identities sum v_K = J+2k+v+q, sum v_I = J+q;
each step >= 1) and tests each sequence against the exact obstruction condition
(c_J = 4^k, d_J = (1-4^k)/3) propagated through the affine recursion of
`lem:affine`. Self-contained (no third-party dependencies). Exits non-zero if any
obstruction is found in a residual cell.
"""
import sys
from fractions import Fraction as F


def check_obstr(vK_seq, vI_seq, k, v):
    """Exact obstruction test: propagate (c, d) through the affine recursion."""
    M = len(vK_seq)
    c = F(1, 1 << v)
    d = F(-1, 1 << v)
    for j in range(M):
        c, d = c * F(1 << vK_seq[j], 1 << vI_seq[j]), (3 * d + c - 1) / F(1 << vI_seq[j])
    return d == F(1 - 4 ** k, 3) and c == F(4 ** k)


def dfs_search(M, k, v, q, vK_max, vI_max):
    """Exhaustive DFS over (v_K, v_I) sequences with the proved structural bounds.

    Returns (found, n_complete): the obstruction list and the number of complete
    length-M sequences whose cumulative sums match (the candidates tested)."""
    target_VK = M + 2 * k + v + q
    target_VI = M + q
    found = []
    n_complete = [0]

    def dfs(j, vK_list, vI_list, sum_vK, sum_vI):
        if j == M:
            if sum_vK == target_VK and sum_vI == target_VI:
                n_complete[0] += 1
                if check_obstr(vK_list, vI_list, k, v):
                    found.append((list(vK_list), list(vI_list)))
            return
        rem_vK, rem_vI, rem_steps = target_VK - sum_vK, target_VI - sum_vI, M - j
        if rem_vK < rem_steps or rem_vI < rem_steps:
            return
        if rem_vK > rem_steps * vK_max or rem_vI > rem_steps * vI_max:
            return
        if j == 0:
            vK_options = [1] if v >= 2 else list(range(2, vK_max + 1))   # K-track prefix / Lemma A
        elif j < v - 1:
            vK_options = [1]                                             # forced prefix
        elif j == v - 1 and v >= 2:
            vK_options = list(range(2, vK_max + 1))                      # prefix gap V_K^v >= v+1
        else:
            vK_options = list(range(1, vK_max + 1))
        for vK in vK_options:
            if vK > rem_vK:
                break
            for vI in range(1, vI_max + 1):
                if vI > rem_vI:
                    break
                vK_list.append(vK)
                vI_list.append(vI)
                dfs(j + 1, vK_list, vI_list, sum_vK + vK, sum_vI + vI)
                vK_list.pop()
                vI_list.pop()

    dfs(0, [], [], 0, 0)
    return found, n_complete[0]


def search(M, k, v, q):
    target_VK = M + 2 * k + v + q
    target_VI = M + q
    vK_max = max(2, target_VK - (M - 1))
    vI_max = max(1, target_VI - (M - 1))
    return dfs_search(M, k, v, q, vK_max=vK_max, vI_max=vI_max)


def close_cells(label, k, J, q_range, v_range):
    total = 0
    searched = 0
    for v in v_range:
        for q in q_range:
            f, n = search(J, k, v, q)
            total += len(f)
            searched += n
    print(f"  {label}: {total} obstructions over {searched} length-{J} sequences "
          f"(v in {list(v_range)}, q in {list(q_range)})", flush=True)
    return total


def main():
    print("=== validation: DFS finds genuine obstructions at the tight depth J=2k+3 ===", flush=True)
    found_any = None
    for v in range(2, 9):
        f, _ = search(9, 3, v, 0)            # s=3 tight at J=9 (q=0)
        if f and found_any is None:
            found_any = (3, 9, v, f[0])
    assert found_any, "machinery broken: no s=3 obstruction at J=9"
    k0, J0, v0, (vK0, vI0) = found_any
    assert check_obstr(vK0, vI0, k0, v0)
    print(f"  e.g. s={k0}, J={J0}, v={v0}: vK={vK0}, vI={vI0}  genuine=True", flush=True)

    print("\n=== claim (lem:dfs-k3): s=3, J=8, q=0, v in [2,8] -> 0 obstructions ===", flush=True)
    t_k3 = close_cells("s=3, J=8, q=0", 3, 8, range(0, 1), range(2, 9))

    print("\n=== claim (s=2 residual): J=5, q in {0,1}, v in [1,5] -> 0 obstructions ===", flush=True)
    t_k2 = close_cells("s=2, J=5, q<=1", 2, 5, range(0, 2), range(1, 6))

    print("\n=== closed-form cross-checks (DFS must also be 0) ===", flush=True)
    close_cells("s=3, J=8, q in {1,2}", 3, 8, range(1, 3), range(2, 9))
    close_cells("s=3, J=7, q=0", 3, 7, range(0, 1), range(2, 8))
    close_cells("s=2, J=5, q=2", 2, 5, range(2, 3), range(1, 6))
    close_cells("s=2, J=4, q in {0,1,2}", 2, 4, range(0, 3), range(1, 5))

    print(f"\nTOTAL obstructions in the residual tails: {t_k3 + t_k2}", flush=True)
    assert t_k3 == 0, f"found {t_k3} obstruction(s) in the s=3 residual gap"
    assert t_k2 == 0, f"found {t_k2} obstruction(s) in the s=2 residual gap"
    print("*** RIGOROUS: positive residual tails closed (s=3: J>=9; s=2 finite part: no J<=5 obstruction) ***",
          flush=True)
    sys.exit(0)


if __name__ == "__main__":
    main()
