#!/usr/bin/env python3
"""Auxiliary: empirical tightness of the depth bound J >= 2|s|+3 (no hard claim).

For every obstruction with |s| >= 2 (the regime where `thm:depth` applies),
records J and the slack J-(2|s|+3), separately for each signed s. Reports, per s,
the minimum J ever seen, the first level L at which that s appears, and the
smallest-slack (tightest) instance with its full (V_K^j, V_I^j) sequence. This
exhibits which strata are tight (slack 0) -- e.g. s=2 and s=-2 are tight at J=7,
witnessed by r=1015979 (s=-2) at L=21 -- and which carry slack, explaining why
the small-|s| tails need the exact carry automaton while large |s| does not.

Produces data only; asserts nothing. Streams per L.
"""
import sys


def v2(n):
    return (n & -n).bit_length() - 1


def reduce_full(r, L):
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


def main():
    Lmax = int(sys.argv[1]) if len(sys.argv) > 1 else 22
    best = {}    # signed s -> (min_slack, J, L, r, v, VK, VI)
    firstL = {}  # signed s -> first L seen
    print(f"scanning obstructions with |s| >= 2, L=5..{Lmax}", flush=True)
    for L in range(5, Lmax + 1):
        cnt = 0
        for r in range(3, (1 << L) + 1, 2):
            res = reduce_full(r, L)
            if res is None:
                continue
            s, J, v, VK, VI = res
            if abs(s) < 2:
                continue
            cnt += 1
            slack = J - (2 * abs(s) + 3)
            firstL.setdefault(s, L)
            if s not in best or slack < best[s][0]:
                best[s] = (slack, J, L, r, v, VK, VI)
        if cnt:
            print(f"  L={L}: {cnt} obstructions with |s| >= 2", flush=True)
    print("\n  s   first L  min J  2|s|+3  min slack   (tightest instance: r, L, v)", flush=True)
    for s in sorted(best):
        slack, J, L, r, v, VK, VI = best[s]
        print(f"{s:<4}  {firstL[s]:<7}  {J:<5}  {2*abs(s)+3:<6}  {slack:<9}  (r={r}, L={L}, v={v})", flush=True)


if __name__ == "__main__":
    main()
