//! Falsifier for thm_no_G0_atom_general (\label{thm:no-G0-atom-general}).
//!
//! For a NOT negative-Mersenne, no shift-zero atom exists on any level: every
//! shift-index-0 obstruction is a lift, not atomic. Non-vacuity is asserted
//! (there ARE shift-zero obstructions, all of them lifts). The negative-
//! Mersenne case is deliberately excluded (a shift-zero J=1 atom does exist
//! there — the companion manuscript's subject); the negative non-Mersenne
//! multipliers (a = -5, -9), which the theorem DOES cover, are included to
//! exercise that regime.
//!
//! Contract: prints CONFIRM <domain> / FALSIFY <reason>; exit 0 / 1.

use or_family_falsifiers::{is_atomic, obstructions, shift_index};
use std::process::exit;

fn fail(m: String) -> ! {
    println!("FALSIFY {m}");
    exit(1);
}

fn main() {
    let mut shift0_seen = 0u64;
    for a in [3i128, 5, 7, 9, 15, -1, -5, -9] {
        for c in [1i128, -1] {
            for level in 3..11u32 {
                let obs = obstructions(level, a, c)
                    .unwrap_or_else(|_| fail(format!("fixed-width overflow a={a} c={c} L={level}")));
                for (r, ep) in obs {
                    if shift_index(&ep, a) == Some(0) {
                        shift0_seen += 1;
                        if is_atomic(r, level, a, c)
                            .unwrap_or_else(|| fail(format!("overflow (atomic) a={a} c={c} L={level}")))
                        {
                            fail(format!("shift-zero ATOM found: a={a} c={c} L={level} r={r}"));
                        }
                    }
                }
            }
        }
    }
    if shift0_seen == 0 {
        fail("vacuous: no shift-zero obstructions enumerated".into());
    }
    println!("CONFIRM no counterexample: {shift0_seen} shift-zero obstructions, all lifts (no G0 atom), over a in {{3,5,7,9,15,-1,-5,-9}}, c in {{1,-1}}, L=3..10");
    exit(0);
}
