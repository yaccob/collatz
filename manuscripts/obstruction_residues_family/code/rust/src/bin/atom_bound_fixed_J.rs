//! Falsifier for prop_atom_bound_fixed_J (\label{prop:atom-J}) -- numeric bound.
//!
//! The number of shift-nonzero atoms at level L with termination index J
//! satisfies |A_L^{(a,b), G != 0}|_J <= C(L-1, J). Counted directly from
//! enumeration; any J whose count exceeds the binomial bound is a refutation.
//! (The determinacy step underpinning the proof is checked symbolically in
//! the companion Python check atom_determinacy.py.)
//!
//! Contract: prints CONFIRM <domain> / FALSIFY <reason>; exit 0 / 1.

use or_family_falsifiers::{is_atomic, obstructions, shift_index};
use std::collections::HashMap;
use std::process::exit;

fn fail(m: String) -> ! {
    println!("FALSIFY {m}");
    exit(1);
}

/// C(n, k) as u128 (n, k small here).
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
    for a in [3i128, 5, 7, -3] {
        for c in [1i128, -1] {
            for level in 5..13u32 {
                let obs = obstructions(level, a, c)
                    .unwrap_or_else(|_| fail(format!("fixed-width overflow a={a} c={c} L={level}")));
                let mut by_j: HashMap<u32, u128> = HashMap::new();
                for (r, ep) in obs {
                    let s = shift_index(&ep, a);
                    if s != Some(0)
                        && s.is_some()
                        && is_atomic(r, level, a, c)
                            .unwrap_or_else(|| fail(format!("overflow (atomic) a={a} c={c} L={level}")))
                    {
                        *by_j.entry(ep.j).or_insert(0) += 1;
                    }
                }
                for (&j, &cnt) in &by_j {
                    let bound = comb(level - 1, j);
                    if cnt > bound {
                        fail(format!(
                            "atom bound exceeded: a={a} c={c} L={level} J={j} count={cnt} > C(L-1,J)={bound}"
                        ));
                    }
                }
            }
        }
    }
    println!("CONFIRM no counterexample: every fixed-J shift-nonzero atom count <= C(L-1,J) over a in {{3,5,7,-3}}, c in {{1,-1}}, L=5..12");
    exit(0);
}
