#!/usr/bin/env python3
"""Empirical confirmation of the depth bound (`thm:depth`) and the shift-index
window (`cor:shift-window`) over all enumerable obstructions.

For every obstruction at level L this script reconstructs its signed shift index
s, termination index J, and parameter v = v_2(r-1) directly from the two T_-
trajectories (independent of the (c,d) recursion), and asserts:

  (depth)        |s| >= 2  =>  J >= 2|s|+3.
  (upper window) s   >= 2  =>  4*s <= L-4-v   (hence s <= floor((L-5)/4)).
  (lower window) s   <= -2 =>  -2*s <= L-4-v  (hence s >= -(L-4-v)/2).

The s in {-1,0,1} classes carry no depth claim (J >= 2|s|+3 is false for |s|<=1,
e.g. r=27 at L=5 has s=1, J=2), so the window bounds are stated for |s| >= 2;
those small classes are the base cases discharged directly. The script also
tabulates the sign distribution and the observed max s vs floor((L-5)/4), which
illustrates that the nontrivial shift support is the O(L) window the corollary
predicts.

Pure integer arithmetic. Exits non-zero on any violation of the three asserted
bounds.
"""
import sys


def v2(n):
    return (n & -n).bit_length() - 1


def shift_depth_v(r, L):
    """Return (s, J, v) if r in Obs_L, else None.  s = shift index, J = depth."""
    if r & 1 == 0 or r == 1:
        return None
    v = v2(r - 1)
    if not (1 <= v < L):
        return None
    a_K, a_I = r, (r - 1) >> v
    V_K, V_I, J = 0, 0, 0
    while True:
        v_K = v2(3 * a_K - 1)
        v_I = v2(3 * a_I - 1)
        if v_K >= L - V_K or v_I >= (L - v) - V_I:
            delta = V_K - V_I - v
            if delta >= 0:
                X1 = (3 * a_I == (1 << delta) * (3 * a_K - 1) + 1)
            else:
                e = -delta
                X1 = ((1 << e) * 3 * a_I == (3 * a_K - 1) + (1 << e))
            if not X1 or delta % 2 != 0:
                return None
            return delta // 2, J, v
        a_K = (3 * a_K - 1) >> v_K
        a_I = (3 * a_I - 1) >> v_I
        V_K += v_K
        V_I += v_I
        J += 1


def main():
    Lmax = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    print("L   #Obs   s<0  s=0  s>0   smin smax   max|s|  floor((L-5)/4)   bounds ok?", flush=True)
    depth_viol = []
    upper_viol = []
    lower_viol = []
    for L in range(5, Lmax + 1):
        neg = zero = pos = 0
        smin, smax, maxabs = 10 ** 9, -10 ** 9, 0
        n = 0
        for r in range(3, (1 << L) + 1, 2):
            res = shift_depth_v(r, L)
            if res is None:
                continue
            s, J, v = res
            n += 1
            neg += s < 0
            zero += s == 0
            pos += s > 0
            smin, smax = min(smin, s), max(smax, s)
            maxabs = max(maxabs, abs(s))
            if abs(s) >= 2 and J < 2 * abs(s) + 3:
                depth_viol.append((r, L, s, J))
            if s >= 2 and 4 * s > L - 4 - v:
                upper_viol.append((r, L, s, v))
            if s <= -2 and -2 * s > L - 4 - v:
                lower_viol.append((r, L, s, v))
        ok = "yes" if not (depth_viol or upper_viol or lower_viol) else "NO"
        print(f"{L:<3} {n:<6} {neg:<4} {zero:<4} {pos:<5} {smin:<4} {smax:<4}  "
              f"{maxabs:<6}  {(L - 5) // 4:<14}  {ok}", flush=True)
    print(f"\ndepth-bound violations (|s|>=2, J<2|s|+3): {depth_viol[:5]} (total {len(depth_viol)})", flush=True)
    print(f"upper-window violations (s>=2, 4s>L-4-v):   {upper_viol[:5]} (total {len(upper_viol)})", flush=True)
    print(f"lower-window violations (s<=-2,-2s>L-4-v):  {lower_viol[:5]} (total {len(lower_viol)})", flush=True)
    assert not depth_viol, f"{len(depth_viol)} depth-bound violations"
    assert not upper_viol, f"{len(upper_viol)} upper-window violations"
    assert not lower_viol, f"{len(lower_viol)} lower-window violations"
    print("\n*** depth bound and shift-index window hold for all obstructions L=5..%d ***" % Lmax, flush=True)
    sys.exit(0)


if __name__ == "__main__":
    main()
