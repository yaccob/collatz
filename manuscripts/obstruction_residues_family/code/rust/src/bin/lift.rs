//! Falsifier for thm_lift (\label{thm:lift}).
//!
//! Every obstruction r at level L has both level-(L+1) lifts r and r+2^L in
//! O_{L+1}, and the lift balance holds exactly:
//!   |O_{L+1}| = 2 |O_L| + |A_{L+1}|  (A = atomic obstructions at L+1).
//!
//! Contract: prints CONFIRM <domain> / FALSIFY <reason>; exit 0 / 1.

use or_family_falsifiers::{is_atomic, obstructions};
use std::collections::HashSet;
use std::process::exit;

fn fail(m: String) -> ! {
    println!("FALSIFY {m}");
    exit(1);
}

fn obs_set(level: u32, a: i128, c: i128) -> Vec<i128> {
    obstructions(level, a, c)
        .unwrap_or_else(|_| fail(format!("fixed-width overflow a={a} c={c} L={level}")))
        .into_iter()
        .map(|(r, _)| r)
        .collect()
}

fn main() {
    for a in [3i128, 5, 7, -1] {
        for c in [1i128, -1] {
            for level in 4..11u32 {
                let ol = obs_set(level, a, c);
                let ol1: HashSet<i128> = obs_set(level + 1, a, c).into_iter().collect();
                for &r in &ol {
                    if !ol1.contains(&r) || !ol1.contains(&(r + (1i128 << level))) {
                        fail(format!("missing lift: a={a} c={c} L={level} r={r}"));
                    }
                }
                let mut atoms = 0usize;
                for &r in &ol1 {
                    if is_atomic(r, level + 1, a, c)
                        .unwrap_or_else(|| fail(format!("overflow (atomic) a={a} c={c} L={}", level + 1)))
                    {
                        atoms += 1;
                    }
                }
                if ol1.len() != 2 * ol.len() + atoms {
                    fail(format!(
                        "lift balance fails: a={a} c={c} L={level} |O_{}|={} != 2*{}+{atoms}",
                        level + 1,
                        ol1.len(),
                        ol.len()
                    ));
                }
            }
        }
    }
    println!("CONFIRM no counterexample: two-lift + balance |O_{{L+1}}|=2|O_L|+|A_{{L+1}}| over a in {{3,5,7,-1}}, c in {{1,-1}}, L=4..10");
    exit(0);
}
