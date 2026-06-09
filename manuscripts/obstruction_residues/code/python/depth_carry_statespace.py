#!/usr/bin/env python3
"""Finite, small state-space certificate for the s=2 carry automaton
(companion to depth_carry_automaton_k2.py, makes the finiteness explicit).

Enumerates the FULL reachable state set under the block-A transition T_A from
R0 = {(C/2, 0, 0)}, and reports the tight carry range, the steady-state interval,
the transient length, and the total number of distinct reachable states
(carry, #f, #g). This is the concrete "small finite" certificate that makes the
fixed-point argument of `lem:carry-automaton` hand-checkable: the whole
reachability graph has at most 185 nodes (at v=1; fewer for v>=2), and the
block-A carry enters the invariant interval [-81, 81] within at most 2 steps.

Exits non-zero if the reachable graph exceeds 185 nodes, if the carry does not
settle into [-81, 81] within 2 block-A steps, or if any per-step increment
exceeds 81 in absolute value (the bound underlying the invariant interval).
"""
import sys


def reachable_statespace(v):
    Icoef = [81, 27, 9, 3, 1]                       # 3^{5-i}, i=1..5
    Kcoef = [3 ** (5 - j) for j in range(v, 6)]     # 3^{5-j}, j=v..5
    nK = len(Kcoef)
    C = 3 ** (6 - v) + 3 ** 5
    assert C % 2 == 0
    R0 = frozenset({(C // 2, 0, 0)})

    def TA(S):  # one block-A position: f+g eligible, no 1-bit (exactly as in the proof)
        out = set()
        for (carry, fi, gj) in S:
            for pf in ((0, 1) if fi < 5 else (0,)):
                for pg in ((0, 1) if gj < nK else (0,)):
                    tot = carry + (Icoef[fi] if pf else 0) - (Kcoef[gj] if pg else 0)
                    if tot & 1:
                        continue
                    out.add((tot >> 1, fi + pf, gj + pg))
        return frozenset(out)

    seq, seen = [R0], {R0: 0}
    union = set(R0)
    while True:
        nxt = TA(seq[-1])
        union |= nxt
        if nxt in seen:
            M0, P = seen[nxt], len(seq) - seen[nxt]
            break
        seen[nxt] = len(seq)
        seq.append(nxt)

    carries = [c for (c, a, b) in union]
    cmin, cmax = min(carries), max(carries)

    def in_steady(S):
        return all(-81 <= c <= 81 for (c, a, b) in S)
    enter = next(m for m in range(len(seq)) if all(in_steady(seq[mm]) for mm in range(m, len(seq))))

    deltas = set()
    for S in seq:
        for (carry, fi, gj) in S:
            for pf in ((0, 1) if fi < 5 else (0,)):
                for pg in ((0, 1) if gj < nK else (0,)):
                    tot = carry + (Icoef[fi] if pf else 0) - (Kcoef[gj] if pg else 0)
                    if tot & 1:
                        continue
                    deltas.add((Icoef[fi] if pf else 0) - (Kcoef[gj] if pg else 0))

    return dict(v=v, M0=M0, P=P, C=C, Cinit=C // 2, n_states=len(union),
                n_carries=len(set(carries)), cmin=cmin, cmax=cmax,
                enter=enter, dmin=min(deltas), dmax=max(deltas))


def main():
    print("v  C    C/2  states  carries  cmin  cmax  enter[-81,81]  delta_range  M0  P", flush=True)
    max_states, max_enter, max_absdelta = 0, 0, 0
    for v in range(1, 7):
        r = reachable_statespace(v)
        max_states = max(max_states, r["n_states"])
        max_enter = max(max_enter, r["enter"])
        max_absdelta = max(max_absdelta, abs(r["dmin"]), abs(r["dmax"]))
        print(f"{r['v']}  {r['C']:<4} {r['Cinit']:<4} {r['n_states']:<6}  "
              f"{r['n_carries']:<7}  {r['cmin']:<4}  {r['cmax']:<4}  "
              f"{r['enter']:<13}  [{r['dmin']},{r['dmax']}]      {r['M0']:<2}  {r['P']}",
              flush=True)
    print(f"\nmax distinct reachable states over all v: {max_states}", flush=True)
    print(f"steady-state interval [-81, 81] entered within {max_enter} block-A steps (all v)", flush=True)
    print(f"max |per-step increment|: {max_absdelta} (<= 81)", flush=True)
    assert max_states <= 185, f"reachable graph has {max_states} > 185 nodes"
    assert max_enter <= 2, f"carry settles only after {max_enter} > 2 block-A steps"
    assert max_absdelta <= 81, f"per-step increment {max_absdelta} exceeds 81"
    sys.exit(0)


if __name__ == "__main__":
    main()
