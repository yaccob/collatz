//! Deep atom-growth enumerator for the empirical alpha(a) discussion
//! (conj_alpha / open_alpha_lt_2) and the deep density lower bounds
//! (rem:deep-scaling, open_correction_factor_universal). It commits and
//! gate-wires the enumeration capability that earlier lived only in an
//! uncommitted local binary.
//!
//! For each multiplier it enumerates O_L by unhacked brute force and, per
//! level, derives the shift-nonzero atom counts |A_L^{G!=0}|_J (split by the
//! termination index J). From these it guards the *proven* facts at deeper L
//! than the existing checks reach, and reports the empirical alpha trajectory.
//!
//! GUARDS (each a FALSIFY of a proven fact):
//!   * density:        |O_L| <= 2^{L-1}            (only odd residues; c_W <= 1/2)
//!   * lift monotone:  |O_L| >= 2|O_{L-1}|         (lift theorem; ratio non-decreasing)
//!   * no-G0 atom:     every atom has shift != 0   (thm_no_G0_atom_general)
//!   * fixed-J bound:  |A_L^{G!=0}|_J <= C(L-1,J)  (prop_atom_bound_fixed_J,
//!                     here verified to a deeper L than atom_bound_fixed_J.rs)
//!   * lift balance:   sum_J |A_L^{G!=0}|_J == |O_L| - 2|O_{L-1}|
//!                     (two independent computations must agree)
//!   * alpha <= 2:     |A_L^{G!=0}| <= 2^{L-1}      (atoms subset odd residues)
//!
//! REPORT (non-gating, empirical): at the deepest level, the alpha root
//! |A_L|^{1/L} and the per-step ratio |A_L|/|A_{L-1}|. These are NOT guarded:
//! the per-step ratio can transiently exceed 2 for small counts near L_min
//! (alpha is the limsup of the L-th root, not the ratio).
//!
//! The brute scan is O(2^L) (Review 014: no sub-2^L method, since obstructions
//! are ~13% dense); rayon + i128 push the cap a few levels past the manuscript
//! L<=24. This binary is therefore a *reach extender and invariant guard*, not
//! a resolver of the open alpha question.
//!
//! Contract: prints `CONFIRM <domain>` (exit 0) or `FALSIFY <reason>` (exit 1).

use clap::Parser;
use or_family_falsifiers::{is_atomic, obstructions, shift_index};
use std::collections::BTreeMap;
use std::process::exit;

#[derive(Parser)]
#[command(name = "atom_growth")]
struct Args {
    /// Comma-separated positive odd multipliers to enumerate.
    #[arg(long, default_value = "3")]
    a: String,
    /// Deepest level to enumerate (brute, O(2^L)).
    #[arg(long, default_value_t = 24)]
    l_cap: u32,
    /// Bias parameter c (= b in the manuscript); counts are c-independent.
    #[arg(long, default_value_t = -1)]
    c: i128,
}

fn fail(m: String) -> ! {
    println!("FALSIFY {m}");
    exit(1);
}

/// C(n, k) as u128 (small here).
fn comb(n: u32, k: u32) -> u128 {
    if k > n {
        return 0;
    }
    let k = k.min(n - k);
    let mut num = 1u128;
    for i in 0..k {
        num = num * (n - i) as u128 / (i + 1) as u128;
    }
    num
}

fn main() {
    let args = Args::parse();
    let c = args.c;
    let multipliers: Vec<i128> = args
        .a
        .split(',')
        .map(|s| s.trim().parse::<i128>().expect("bad --a value"))
        .collect();

    let mut report: Vec<String> = Vec::new();

    for a in multipliers {
        // |O_L| and shift-nonzero atom counts by J, per level.
        let mut card: BTreeMap<u32, u128> = BTreeMap::new();
        let mut atoms_total: BTreeMap<u32, u128> = BTreeMap::new();
        let mut last_level_by_j: BTreeMap<u32, u128> = BTreeMap::new();

        for level in 4..=args.l_cap {
            let obs = obstructions(level, a, c)
                .unwrap_or_else(|_| fail(format!("fixed-width overflow a={a} c={c} L={level}")));
            let n = obs.len() as u128;
            card.insert(level, n);

            // density: only odd residues can be obstructions.
            if n > (1u128 << (level - 1)) {
                fail(format!(
                    "a={a} L={level}: |O_L|={n} > 2^(L-1)={} (density > 1/2)",
                    1u128 << (level - 1)
                ));
            }

            // per-J shift-nonzero atom counts; detect any shift-zero atom.
            let mut by_j: BTreeMap<u32, u128> = BTreeMap::new();
            let mut atoms = 0u128;
            for (r, ep) in &obs {
                let atomic = is_atomic(*r, level, a, c)
                    .unwrap_or_else(|| fail(format!("overflow (atomic) a={a} c={c} L={level}")));
                if !atomic {
                    continue;
                }
                match shift_index(ep, a) {
                    Some(0) => fail(format!(
                        "a={a} L={level}: shift-zero ATOM at r={r} (no-G0-atom theorem violated)"
                    )),
                    Some(_) => {
                        *by_j.entry(ep.j).or_insert(0) += 1;
                        atoms += 1;
                    }
                    None => fail(format!(
                        "a={a} L={level}: order-lemma violation (e does not divide delta) at r={r}"
                    )),
                }
            }
            atoms_total.insert(level, atoms);

            // fixed-J bound (proven), at deeper L than atom_bound_fixed_J.rs.
            for (&j, &cnt) in &by_j {
                let bound = comb(level - 1, j);
                if cnt > bound {
                    fail(format!(
                        "a={a} L={level} J={j}: atom count {cnt} > C(L-1,J)={bound}"
                    ));
                }
            }

            // lift monotonicity + balance: |O_L| = 2|O_{L-1}| + |A_L| (no G0 atoms).
            if let Some(&prev) = card.get(&(level - 1)) {
                if n < 2 * prev {
                    fail(format!(
                        "a={a} L={level}: |O_L|={n} < 2|O_(L-1)|={} (lift monotonicity)",
                        2 * prev
                    ));
                }
                if n - 2 * prev != atoms {
                    fail(format!(
                        "a={a} L={level}: lift balance broken: |O_L|-2|O_(L-1)|={} != sum_J atoms={atoms}",
                        n - 2 * prev
                    ));
                }
            }

            if level == args.l_cap {
                last_level_by_j = by_j;
            }
        }

        // empirical alpha at the deepest two informative levels.
        let top = args.l_cap;
        let a_top = *atoms_total.get(&top).unwrap_or(&0);
        let a_prev = *atoms_total.get(&(top - 1)).unwrap_or(&0);
        let ratio = if a_prev > 0 {
            a_top as f64 / a_prev as f64
        } else {
            0.0
        };
        let root = if a_top > 0 {
            (a_top as f64).powf(1.0 / top as f64)
        } else {
            0.0
        };
        // NOTE: the per-step ratio |A_L|/|A_(L-1)| is reported, NOT guarded: it
        // can transiently exceed 2 for small counts near L_min (e.g. a=5), which
        // does NOT contradict alpha = limsup |A_L|^{1/L} <= 2. The proven alpha<=2
        // is the bound |A_L| <= 2^{L-1} (atoms subset odd residues), guarded next.
        if a_top > (1u128 << (top - 1)) {
            fail(format!(
                "a={a} L={top}: |A_L|={a_top} > 2^(L-1)={} (alpha <= 2 violated)",
                1u128 << (top - 1)
            ));
        }
        let jdist: Vec<String> = last_level_by_j
            .iter()
            .map(|(j, n)| format!("J{j}:{n}"))
            .collect();
        report.push(format!(
            "a={a}: |O_{top}|={}, |A_{top}|={a_top}, alpha-ratio={ratio:.4}, alpha-root={root:.4}, top-J-dist[{}]",
            card.get(&top).unwrap_or(&0),
            jdist.join(",")
        ));
    }

    println!(
        "CONFIRM no counterexample: density<=1/2, lift balance, no-G0 atom, fixed-J bound C(L-1,J), and alpha<2 hold to L={}, c={c}; {}",
        args.l_cap,
        report.join(" | ")
    );
    exit(0);
}
