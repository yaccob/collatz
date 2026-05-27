//! Falsifier for thm_Lmin_lower (\label{thm:Lmin-lower}).
//!
//! Lower bound L_min(a) >= e+1 (e = ord_{|a|}(2)) for a outside the
//! negative-Mersenne case, in its strongest finite form: O_L is empty for
//! every L <= e, forcing the smallest non-empty level to be >= e+1.
//!
//! Also guards the EXACT first-obstruction levels stated in the sec:Lmin
//! proof prose: the Mersenne multipliers {3,7,15,31} have L_min = 2e+1
//! exactly, and L_min(5) = 11, L_min(21) = 10 (the bound e+1 is not tight).
//!
//! Contract: prints CONFIRM <domain> / FALSIFY <reason>; exit 0 / 1.

use or_family_falsifiers::{obstructions, ord2};
use std::process::exit;

fn fail(m: String) -> ! {
    println!("FALSIFY {m}");
    exit(1);
}

fn main() {
    for a in [3i128, 5, 7, 9, 15] {
        let e = ord2(a);
        for c in [1i128, -1] {
            for level in 1..=e {
                let obs = obstructions(level, a, c)
                    .unwrap_or_else(|_| fail(format!("fixed-width overflow a={a} c={c} L={level}")));
                if !obs.is_empty() {
                    let rs: Vec<i128> = obs.iter().take(5).map(|&(r, _)| r).collect();
                    fail(format!(
                        "O_L non-empty at L={level} <= e={e} (a={a} c={c}): {rs:?} -- L_min < e+1"
                    ));
                }
            }
        }
    }
    // Exact L_min(a) stated in the sec:Lmin proof prose (b = -1; the value is
    // b-independent by conjugation). L_min is the first non-empty level; since
    // O_L is empty for L <= e (proven above), scan upward from e+1.
    for (a, exp_lmin) in [(3i128, 5u32), (5, 11), (7, 7), (15, 9), (21, 10), (31, 11)] {
        let e = ord2(a);
        let mut lmin = None;
        for level in (e + 1)..=exp_lmin {
            let obs = obstructions(level, a, -1)
                .unwrap_or_else(|_| fail(format!("fixed-width overflow a={a} L={level}")));
            if !obs.is_empty() {
                lmin = Some(level);
                break;
            }
        }
        match lmin {
            Some(l) if l == exp_lmin => {}
            Some(l) => fail(format!("L_min({a})={l} != stated {exp_lmin}")),
            None => fail(format!("L_min({a}) > stated {exp_lmin} (no obstruction at e+1..={exp_lmin})")),
        }
        if [3, 7, 15, 31].contains(&a) && exp_lmin != 2 * e + 1 {
            fail(format!("a={a} Mersenne: stated L_min {exp_lmin} != 2e+1={}", 2 * e + 1));
        }
    }
    println!("CONFIRM no counterexample: O_L empty for all L<=e (a in {{3,5,7,9,15}}, c in {{1,-1}}, so L_min >= e+1); exact L_min = 5/11/7/9/10/11 for a = 3/5/7/15/21/31 (Mersenne 3,7,15,31 at 2e+1)");
    exit(0);
}
