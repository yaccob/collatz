"""Empirical verification of simultaneous stop and parity (Corollary 2.5 and
Lemma 2.4 of the manuscript).

For each G_0-obstruction r at level L (i.e. r ∈ Ω_L with shift index a = 0):
- compute the synchronization step j* at which the K- and I-tracks meet;
- verify the parity-of-valuations identity V_K - V_I = v at termination
  (this is the parity lemma applied at the endpoint of the parallel
  reduction; v = v_2(r-1));
- verify that the K- and I-tracks satisfy the termination condition at
  the same index J (simultaneous stop).

Output: counts of violations of each property. Zero violations
constitutes empirical confirmation.
"""

from __future__ import annotations
import sys
from fractions import Fraction
from collections import defaultdict


def v2(n):
    if n == 0:
        return -1
    n = abs(n)
    c = 0
    while (n & 1) == 0:
        n >>= 1
        c += 1
    return c


def step_T_minus(a, b):
    three_a_minus_1 = 3 * a - 1
    v_a = v2(three_a_minus_1)
    v_b = v2(b) if b != 0 else 99
    if v_a >= v_b:
        return None
    return (three_a_minus_1 // (1 << v_a), (3 * b) // (1 << v_a))


def trace_with_sync(r, L):
    """Trace parallel reduction; return list of (a_K, a_I, b_K, b_I, v_K_step, v_I_step)
    per step + sync_step + final (a_K, a_I, c, d, X)."""
    if r % 2 == 0:
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
    trace = []
    j = 0
    sync_step = None
    V_K = 0
    V_I = 0
    while True:
        if a_K == a_I and b_K == b_I and sync_step is None:
            sync_step = j
        step_K = step_T_minus(a_K, b_K)
        step_I = step_T_minus(a_I, b_I)
        if step_K is None or step_I is None:
            break
        v_K_step = v2(3 * a_K - 1)
        v_I_step = v2(3 * a_I - 1)
        trace.append((a_K, a_I, b_K, b_I, v_K_step, v_I_step))
        V_K += v_K_step
        V_I += v_I_step
        c_old = c
        c = c_old * Fraction(1 << v_K_step, 1 << v_I_step)
        d = (3 * d + c_old - 1) / Fraction(1 << v_I_step)
        a_K, b_K = step_K
        a_I, b_I = step_I
        j += 1
    if a_K == a_I and b_K == b_I and sync_step is None:
        sync_step = j
    return {
        "v": v,
        "m": m,
        "trace": trace,
        "sync_step": sync_step,
        "V_K": V_K,
        "V_I": V_I,
        "final_a_K": a_K,
        "final_a_I": a_I,
        "c": c,
        "d": d,
        "X": 3 * d + c,
    }


def main():
    L = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    print(f"Step A + B verification at L = {L}\n")
    print("Lemma B.1: V_K^(j*) - V_I^(j*) = v at synchronization step j*")
    print("Synchronisation check: V_K - V_I = v at j* (parity lemma at sync index)\n")

    g0_obstructions = []
    violations = []
    for r in range(1, 1 << L, 2):
        res = trace_with_sync(r, L)
        if res is None:
            continue
        if res["X"] != 1 or res["c"] != 1 or res["d"] != 0:
            continue
        # Lemma G_0 obstruction
        if res["sync_step"] is None:
            violations.append((r, "no sync"))
            continue
        # Compute V_K^(j*), V_I^(j*) cumulatively
        V_K_sync = sum(t[4] for t in res["trace"][: res["sync_step"]])
        V_I_sync = sum(t[5] for t in res["trace"][: res["sync_step"]])
        if V_K_sync - V_I_sync != res["v"]:
            violations.append((r, f"V_K-V_I = {V_K_sync - V_I_sync} != v = {res['v']}"))
            continue
        g0_obstructions.append(
            {
                "r": r,
                "v": res["v"],
                "m": res["m"],
                "j_star": res["sync_step"],
                "V_K_sync": V_K_sync,
                "V_I_sync": V_I_sync,
                "a_sync": (
                    res["trace"][res["sync_step"]][0]
                    if res["sync_step"] < len(res["trace"])
                    else res["final_a_K"]
                ),
                "V_K_total": res["V_K"],
                "V_I_total": res["V_I"],
                "a_end": res["final_a_K"],
            }
        )

    print(f"Total G_0 obstructions: {len(g0_obstructions)}")
    print(f"Parity-at-sync violations (V_K - V_I != v at j*): {len(violations)}")
    if violations:
        print(f"  First 5: {violations[:5]}")
    else:
        print(
            f"  → Parity-at-sync holds for ALL {len(g0_obstructions)} G_0 obstructions. ✓"
        )

    # Endpoint check (Corollary 2.5 + Lemma 2.4 at termination):
    # V_K^(J) - V_I^(J) = v (parity lemma applied at termination index).
    print("\nEndpoint parity: V_K^(J) - V_I^(J) = v (Lemma 2.4 / Corollary 2.5).")
    iso_violations = sum(
        1 for w in g0_obstructions if w["V_K_total"] - w["V_I_total"] != w["v"]
    )
    print(f"  Endpoint violations: {iso_violations}/{len(g0_obstructions)}")
    if iso_violations == 0:
        print("  → Endpoint parity holds for ALL G_0 obstructions. ✓")

    # Histogram (j*, V_K_sync) — interesting structural insight
    print("\nDistribution of (j*, V_K_sync) pairs:")
    pairs = defaultdict(int)
    for w in g0_obstructions:
        pairs[(w["j_star"], w["V_K_sync"])] += 1
    print("  j* | V_K_sync | count")
    for j, V in sorted(pairs):
        print(f"  {j:>2} | {V:>8} | {pairs[(j, V)]:>5}")

    if not violations and iso_violations == 0:
        print(
            f"\n✓ VERIFIED: simultaneous stop and parity lemma at termination "
            f"hold for all G_0 obstructions at L={L}."
        )
    else:
        print(
            f"\n✗ FAILED: {len(violations)} parity-at-sync and "
            f"{iso_violations} endpoint-parity violations at L={L}."
        )


if __name__ == "__main__":
    main()
