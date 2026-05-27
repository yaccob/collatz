//! Falsifier for KG asset `prop_J1_characterization`.
//!
//! It tries to REFUTE the corrected J=1 criterion by searching for a
//! counterexample over the widest feasible domain. It never proves anything;
//! a non-failing run means only "no counterexample in the searched domain".
//!
//! Corrected criterion (manuscript "Characterisation of J=1 atoms"):
//!   for positive odd a >= 3, e := ord_a(2), k_a := (2^e - 1)/a, an atomic
//!   obstruction with termination index J = 1 exists at some level L <= 2e+1
//!   IFF  a - 1 + 2^v = 2^w k_a  has integers v >= 1, v+1 <= w <= e;
//!   the atom then sits at level w+e+1 with shift s = 1 and V_I^{(1)} = w-v.
//!
//! Two directions, each over its own widest feasible domain:
//!   * NECESSITY  — a fixed-width sweep of all odd residues at every level
//!     up to 2e+1 (for a with 2e+1 <= --l-cap): every J=1 atom found must
//!     satisfy the criterion, and atoms exist iff the criterion is solvable.
//!   * REALISABILITY (the heart of C-01) — for every odd a up to --a-max and
//!     every criterion solution (v,w), CONSTRUCT the seed
//!     r = a^{-1}(2^{w+e} - c) mod 2^{w+e+1} and confirm it is a J=1 atom.
//!     This is O(#solutions), with no 2^L sweep, so it reaches enormous a.
//!
//! Performance: all arithmetic is fixed-width i128 with *checked* overflow
//! (an out-of-range case is reported and skipped, never silently wrapped — a
//! silent overflow in a falsifier manufactures false confidence). J=1 atom
//! detection needs at most two reduction steps, and atomicity uses the proven
//! equivalence "J=1 atom  <=>  V_K^{(1)} = L-1" (for a>0: V_K^{(1)} < L-1 makes
//! r a lift, and V_K^{(1)} = L-1 forces the level-(L-1) reduction to stop at
//! index 0, where Phi_0 != 0), so no level-(L-1) reduction is run. `rayon`
//! parallelises the necessity sweep.
//!
//! Contract: prints exactly `CONFIRM <domain>` (exit 0) or `FALSIFY <reason>`
//! (exit 1). Deterministic.

use clap::Parser;
use or_family_falsifiers::{fma, pow2, v2};
use rayon::prelude::*;
use std::process::exit;

#[derive(Parser)]
#[command(name = "j1_characterization")]
struct Args {
    /// Necessity sweep: skip a whose feasible window 2e+1 exceeds this.
    #[arg(long, default_value_t = 14)]
    l_cap: u32,
    /// Realisability construction: largest odd multiplier a to test.
    #[arg(long, default_value_t = 100_000)]
    a_max: u64,
    /// Bias parameter c (= b in the manuscript); criterion is c-independent.
    #[arg(long, default_value_t = -1)]
    c: i128,
}

/// Multiplicative order e = ord_{a}(2) for odd a > 1.
fn ord2(a: u64) -> u32 {
    if a == 1 {
        return 1;
    }
    let (mut k, mut x) = (1u32, 2u64 % a);
    while x != 1 {
        x = (x * 2) % a;
        k += 1;
    }
    k
}

enum Class {
    Atom { v: u32, w: u32 }, // J=1 atomic obstruction
    Other,                   // ineligible / not J=1 / not obstruction / not atom
    Overflow,                // outside the fixed-width regime
}

/// Classify residue r at level L for T_{a,c}: is it a J=1 atom?
/// At most two reduction steps; atomicity via V_K^{(1)} = L-1.
fn classify(r: i128, level: u32, a: i128, c: i128) -> Class {
    macro_rules! ovf {
        ($e:expr) => {
            match $e {
                Some(x) => x,
                None => return Class::Overflow,
            }
        };
    }
    let s = r + c;
    if s == 0 {
        return Class::Other;
    }
    let v = v2(s);
    if v == 0 || v >= level {
        return Class::Other;
    }
    let m = s >> v;

    // --- step 0 ---
    let ak0 = ovf!(fma(a, r, c)); // A_K^{(0)} = a r + c
    let ai0 = ovf!(fma(a, m, c)); // A_I^{(0)} = a m + c
    let vk0 = v2(ak0);
    let vi0 = v2(ai0);
    // step 0 must fire: v_K^{(0)} < L and v_I^{(0)} < L - v (else J = 0).
    if vk0 >= level || vi0 >= level - v {
        return Class::Other;
    }
    let big_vk1 = vk0; // V_K^{(1)}
    let big_vi1 = vi0; // V_I^{(1)}

    // --- does step 1 fire? (if so, J >= 2) ---
    let ak1 = ak0 >> vk0; // a_K^{(1)}
    let ai1 = ai0 >> vi0; // a_I^{(1)}
    let ak1n = ovf!(fma(a, ak1, c));
    let ai1n = ovf!(fma(a, ai1, c));
    let vk1 = v2(ak1n);
    let vi1 = v2(ai1n);
    let res_k1 = level - big_vk1; // v2(b_K) at index 1
    let res_i1 = (level - v) - big_vi1; // v2(b_I) at index 1
    if vk1 < res_k1 && vi1 < res_i1 {
        return Class::Other; // step 1 fires => J >= 2
    }

    // --- J = 1: obstruction test via the D-recurrence ---
    // D_0 = c; X_0 = 2^0 - 2^{0+v} = 1 - 2^v; D_1 = a D_0 - c X_0.
    let x0 = 1 - ovf!(pow2(v));
    let d1 = ovf!(fma(a, c, 0)) - c * x0; // a*c - c*x0 (small)
    // X_1 = 2^{V_K^{(1)}} - 2^{V_I^{(1)} + v}; obstruction <=> a D_1 - c X_1 = 0.
    let x1 = ovf!(pow2(big_vk1)) - ovf!(pow2(big_vi1 + v));
    let lhs = ovf!(a.checked_mul(d1)) - ovf!(c.checked_mul(x1));
    if lhs != 0 {
        return Class::Other; // J=1 but not an obstruction
    }
    // atomic <=> V_K^{(1)} = L - 1 (proven equivalence for a > 0).
    if big_vk1 != level - 1 {
        return Class::Other; // a lift, not atomic
    }
    Class::Atom {
        v,
        w: big_vi1 + v,
    }
}

/// Modular inverse of odd `a` modulo 2^k (k <= 126), via Newton iteration.
fn inv_mod_2k(a: i128, k: u32) -> i128 {
    let mask = (1i128 << k) - 1;
    let a = a & mask;
    let mut x = 1i128; // a is odd => x0 = 1 is a 1-bit-correct inverse
    // each step doubles the number of correct bits: x <- x(2 - a x) mod 2^k
    let mut bits = 1u32;
    while bits < k {
        // wrapping_mul gives the correct low 128 bits; mask to k bits.
        let ax = a.wrapping_mul(x) & mask;
        x = x.wrapping_mul((2 - ax) & mask) & mask;
        bits *= 2;
    }
    x & mask
}

/// All (v, w) solving a-1+2^v = 2^w k_a with v>=1, v+1<=w<=e, using i128.
/// Returns None if 2^e overflows the fixed-width regime.
fn criterion_solutions(a: u64, e: u32, k_a: i128) -> Option<Vec<(u32, u32)>> {
    let mut out = Vec::new();
    for v in 1..e {
        let val = (a as i128 - 1) + pow2(v)?;
        if val % k_a != 0 {
            continue;
        }
        let q = val / k_a;
        if q >= 1 && (q & (q - 1)) == 0 {
            let w = q.trailing_zeros();
            if w >= v + 1 && w <= e {
                out.push((v, w));
            }
        }
    }
    Some(out)
}

fn fail(msg: String) -> ! {
    println!("FALSIFY {msg}");
    exit(1);
}

/// Necessity: every J=1 atom up to level 2e+1 (brute force, fixed width).
fn sweep_atoms(a: u64, top: u32, c: i128) -> Vec<(u64, u32, u32, u32)> {
    let ai = a as i128;
    (5..=top)
        .into_par_iter()
        .flat_map_iter(|level| {
            (0..(1u64 << (level - 1))).filter_map(move |i| {
                let r = 2 * i + 1;
                match classify(r as i128, level, ai, c) {
                    Class::Atom { v, w } => Some((r, level, v, w)),
                    Class::Overflow => Some((u64::MAX, level, 0, 0)), // sentinel
                    Class::Other => None,
                }
            })
        })
        .collect()
}

fn main() {
    let args = Args::parse();
    let c = args.c;

    // ---- (0) reproduce known instances by CONSTRUCTION -------------------
    // a=3 (v=1,w=2) -> r=27 at L=5; a=21 (v=2,w=3) -> r=317 at L=10.
    for (a, v, w, want) in [(3u64, 1u32, 2u32, 27i128), (21, 2, 3, 317)] {
        let e = ord2(a);
        let level = w + e + 1;
        let k = level + 1;
        let r = (inv_mod_2k(a as i128, k)
            .wrapping_mul(((1i128 << (w + e)) - c) & ((1i128 << k) - 1)))
            & ((1i128 << k) - 1);
        if r != want {
            fail(format!("reproduce: a={a} (v={v},w={w}) constructed r={r}, expected {want}"));
        }
        match classify(r, level, a as i128, c) {
            Class::Atom { v: cv, w: cw } if cv == v && cw == w => {}
            _ => fail(format!("reproduce: constructed r={r} for a={a} is not the J=1 atom (v={v},w={w})")),
        }
    }

    // ---- (1) realisability by construction over a huge range -------------
    let mut constructed = 0u64;
    let mut ovf_skipped = 0u64;
    let mut a = 3u64;
    while a <= args.a_max {
        let e = ord2(a);
        let kpow = match pow2(e) {
            Some(x) => x,
            None => {
                ovf_skipped += 1;
                a += 2;
                continue;
            }
        };
        let k_a = (kpow - 1) / a as i128;
        let sols = match criterion_solutions(a, e, k_a) {
            Some(s) => s,
            None => {
                ovf_skipped += 1;
                a += 2;
                continue;
            }
        };
        for (v, w) in sols {
            let level = w + e + 1;
            let k = level + 1;
            if k >= 126 {
                ovf_skipped += 1;
                continue;
            }
            let mask = (1i128 << k) - 1;
            let r = (inv_mod_2k(a as i128, k).wrapping_mul(((1i128 << (w + e)) - c) & mask)) & mask;
            match classify(r, level, a as i128, c) {
                Class::Atom { v: cv, w: cw } if cv == v && cw == w => constructed += 1,
                Class::Overflow => ovf_skipped += 1,
                _ => fail(format!(
                    "a={a}: criterion solution (v={v},w={w}) constructs r={r} at L={level} that is NOT a J=1 atom (realisability gap)"
                )),
            }
        }
        a += 2;
    }

    // ---- (2) necessity sweep over the feasibility-driven window ----------
    let mut swept: Vec<u64> = Vec::new();
    let mut a = 3u64;
    while a <= 63 {
        let e = ord2(a);
        let top = 2 * e + 1;
        if top <= args.l_cap {
            let k_a = (pow2(e).unwrap() - 1) / a as i128;
            let sols = criterion_solutions(a, e, k_a).unwrap();
            let atoms = sweep_atoms(a, top, c);
            if atoms.iter().any(|&(r, ..)| r == u64::MAX) {
                fail(format!("a={a}: fixed-width overflow during necessity sweep"));
            }
            if sols.is_empty() != atoms.is_empty() {
                fail(format!(
                    "a={a}: criterion solvable={} but J=1 atom exists={} (sols={sols:?})",
                    !sols.is_empty(),
                    !atoms.is_empty()
                ));
            }
            for &(r, level, v, w) in &atoms {
                let lhs = (a as i128 - 1) + (1i128 << v);
                if lhs != (1i128 << w) * k_a {
                    fail(format!(
                        "a={a}: J=1 atom r={r} at L={level} has (v={v},w={w}) violating the criterion"
                    ));
                }
            }
            swept.push(a);
        }
        a += 2;
    }

    println!(
        "CONFIRM no counterexample: realisability constructed+verified {constructed} atoms for odd a<={} ({ovf_skipped} solutions skipped as out of the fixed-width regime); necessity swept a in {{{}}} (2e+1 <= l_cap={}), c={c}",
        args.a_max,
        swept.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(","),
        args.l_cap,
    );
}
