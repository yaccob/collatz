//! Falsifier for lem_order_lemma (\label{lem:order-lemma}) and, as the same
//! divisibility, cor_sync_general (\label{cor:sync-general}).
//!
//! For every obstruction residue r at level L with termination index J, the
//! order e := ord_{|a|}(2) divides delta_J = V_K - V_I - v (so shift_index is
//! always an integer). The parallel reduction drives both tracks in one loop,
//! so same-index termination is structural; this falsifies the divisibility.
//!
//! Contract: prints CONFIRM <domain> / FALSIFY <reason>; exit 0 / 1.

use or_family_falsifiers::{obstructions, shift_index};
use std::process::exit;

fn fail(m: String) -> ! {
    println!("FALSIFY {m}");
    exit(1);
}

fn main() {
    let mut tested = 0u64;
    for a in [3i128, 5, 7, 9, 15, -1, -3, -5, -9] {
        for c in [1i128, -1] {
            for level in 3..12u32 {
                let obs = obstructions(level, a, c)
                    .unwrap_or_else(|_| fail(format!("fixed-width overflow at a={a} c={c} L={level}")));
                for (r, ep) in obs {
                    tested += 1;
                    if shift_index(&ep, a).is_none() {
                        let delta = ep.v_k as i64 - ep.v_i as i64 - ep.v as i64;
                        fail(format!(
                            "order lemma violated: a={a} c={c} L={level} r={r} delta_J={delta} not divisible by e=ord_|a|(2)"
                        ));
                    }
                }
            }
        }
    }
    if tested == 0 {
        fail("vacuous: no obstructions enumerated".into());
    }
    println!("CONFIRM no counterexample: {tested} obstructions over a in {{3,5,7,9,15,-1,-3,-5,-9}}, c in {{1,-1}}, L=3..11");
    exit(0);
}
