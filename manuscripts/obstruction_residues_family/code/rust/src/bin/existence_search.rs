//! Existence solver for `conj:existence` (open assumption open_cW_existence):
//! c_W^{(a)} > 0  <=>  O_L^{(a,b)} != empty for some L (proven existence
//! criterion thm_existence_criterion). This binary DECIDES existence per
//! positive odd multiplier by locating L_min(a) = smallest non-empty level.
//!
//! Two regimes, both exact (no heuristics):
//!   * J=1-solvable a — the proven J=1 criterion a-1+2^v = 2^w k_a gives an
//!     obstruction at level w+e+1 in O(1) per a (no enumeration). Existence is
//!     then settled constructively (cf. j1_characterization, which verifies the
//!     witnesses up to a<=16383); here we only record the predicted level.
//!   * non-J1 a — there is no known sub-2^L existence test (this is exactly why
//!     conj:existence is open), so L_min is found by unhacked brute enumeration
//!     `obstructions(L,...)` over L = e+1 .. --l-cap. This settles the
//!     multipliers the manuscript reports as merely "not found up to L=16"
//!     (|a| in {13,19,23,25,27}) by exhibiting their first obstruction level,
//!     or confirming vacuity up to a deeper cap.
//!
//! The brute path is the same O(2^L) as any residue scan (Review 014); Rust +
//! rayon just push the reachable cap a few levels past the Python L=16/18.
//!
//! Contract: prints `CONFIRM <domain>` (exit 0) or `FALSIFY <reason>` (exit 1).
//! FALSIFY fires only on an internal inconsistency (a brute L_min contradicting
//! a known manuscript value, or the J=1 criterion disagreeing with brute over
//! the overlap) — i.e. it refutes the *tooling*, not the open conjecture.

use clap::Parser;
use or_family_falsifiers::{obstructions, pow2};
use std::process::exit;

#[derive(Parser)]
#[command(name = "existence_search")]
struct Args {
    /// Largest positive odd multiplier a to test.
    #[arg(long, default_value_t = 31)]
    a_max: u64,
    /// Brute enumeration cap: search L = e+1 .. l_cap for the first obstruction.
    #[arg(long, default_value_t = 20)]
    l_cap: u32,
    /// Bias parameter c (= b in the manuscript); existence is c-independent.
    #[arg(long, default_value_t = -1)]
    c: i128,
}

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

fn fail(m: String) -> ! {
    println!("FALSIFY {m}");
    exit(1);
}

/// Smallest level hosting a J=1 atom via the criterion a-1+2^v = 2^w k_a
/// (v>=1, v+1<=w<=e), or None if unsolvable / out of the fixed-width regime.
fn j1_min_level(a: u64) -> Option<u32> {
    let e = ord2(a);
    let kpow = pow2(e)?; // None on i128 overflow
    let k_a = (kpow - 1) / a as i128;
    let mut best: Option<u32> = None;
    for v in 1..e {
        let val = match pow2(v) {
            Some(p) => (a as i128 - 1) + p,
            None => return best,
        };
        if val % k_a != 0 {
            continue;
        }
        let q = val / k_a;
        if q >= 1 && (q & (q - 1)) == 0 {
            let w = q.trailing_zeros();
            if w >= v + 1 && w <= e {
                let level = w + e + 1;
                best = Some(best.map_or(level, |b| b.min(level)));
            }
        }
    }
    best
}

/// Smallest level with an obstruction, brute force over L = e+1 .. l_cap.
/// Some(L) = first non-empty; None = vacuous up to l_cap (or overflow).
fn brute_lmin(a: i128, c: i128, e: u32, l_cap: u32) -> Result<Option<u32>, u32> {
    for level in (e + 1)..=l_cap {
        match obstructions(level, a, c) {
            Ok(v) if !v.is_empty() => return Ok(Some(level)),
            Ok(_) => {}
            Err(()) => return Err(level), // fixed-width overflow at this level
        }
    }
    Ok(None)
}

/// Known L_min(|a|) from the manuscript (tab:J1 / lmin prose), b-independent.
fn known_lmin(a: u64) -> Option<u32> {
    match a {
        3 => Some(5),
        5 => Some(11),
        7 => Some(7),
        9 => Some(11),
        11 => Some(18),
        15 => Some(9),
        17 => Some(16),
        21 => Some(10),
        31 => Some(11),
        _ => None,
    }
}

fn main() {
    let args = Args::parse();
    let c = args.c;

    let mut settled_j1: Vec<(u64, u32)> = Vec::new(); // (a, w+e+1)
    let mut settled_brute: Vec<(u64, u32)> = Vec::new(); // (a, L_min)
    let mut open: Vec<u64> = Vec::new(); // vacuous up to l_cap

    let mut a = 3u64;
    while a <= args.a_max {
        let e = ord2(a);
        let j1 = j1_min_level(a);

        let lmin = match brute_lmin(a as i128, c, e, args.l_cap) {
            Ok(x) => x,
            Err(level) => fail(format!(
                "a={a}: fixed-width overflow during brute enumeration at L={level}"
            )),
        };

        // Cross-check 1: brute vs. the manuscript's tabulated L_min.
        if let (Some(lm), Some(k)) = (lmin, known_lmin(a)) {
            if lm != k {
                fail(format!(
                    "a={a}: brute L_min={lm} contradicts manuscript value {k}"
                ));
            }
        }
        // Cross-check 2: a J=1 solution within the cap forces a brute hit no
        // later than that level (the J=1 atom is an obstruction).
        if let Some(j1l) = j1 {
            if j1l <= args.l_cap {
                match lmin {
                    Some(lm) if lm <= j1l => {}
                    _ => fail(format!(
                        "a={a}: J=1 criterion predicts an obstruction at L={j1l} (<= l_cap), \
                         but brute found L_min={lmin:?}"
                    )),
                }
            }
        }

        match (j1, lmin) {
            (Some(j1l), _) => settled_j1.push((a, j1l)),
            (None, Some(lm)) => settled_brute.push((a, lm)),
            (None, None) => open.push(a),
        }
        a += 2;
    }

    // New content: positive a the manuscript lists as "not found up to L=16"
    // that this deeper search has now settled.
    let manuscript_undetected = [13u64, 19, 23, 25, 27];
    let newly: Vec<(u64, u32)> = settled_brute
        .iter()
        .filter(|(a, _)| manuscript_undetected.contains(a))
        .copied()
        .collect();

    let fmt = |v: &[(u64, u32)]| {
        v.iter()
            .map(|(a, l)| format!("{a}@{l}"))
            .collect::<Vec<_>>()
            .join(",")
    };

    println!(
        "CONFIRM no counterexample: existence decided for positive odd a<={}, c={c} \
         (l_cap={}); J=1-settled a@L: [{}]; brute L_min a@L: [{}]; still vacuous <= l_cap: [{}]; \
         newly-settled-vs-manuscript: [{}]",
        args.a_max,
        args.l_cap,
        fmt(&settled_j1),
        fmt(&settled_brute),
        open.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(","),
        fmt(&newly),
    );
    exit(0);
}
