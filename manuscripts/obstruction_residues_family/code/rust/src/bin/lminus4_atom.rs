//! Falsifier for thm_Lminus4_atom_a3 (\label{thm:Lminus4-atom}).
//!
//! For a=3, b=-1 and every even L >= 6, r = 2^{L-2} + 3 is an atomic
//! obstruction with termination index J = L-4 and shift index 1. For odd L
//! the same r is NOT an obstruction (its trace gives an odd delta_J).
//!
//! Contract: prints CONFIRM <domain> / FALSIFY <reason>; exit 0 / 1.

use or_family_falsifiers::{is_atomic, is_obstruction, reduce, shift_index, Reduced};
use std::process::exit;

fn fail(m: String) -> ! {
    println!("FALSIFY {m}");
    exit(1);
}

fn main() {
    for level in [6u32, 8, 10, 12] {
        let r = (1i128 << (level - 2)) + 3;
        let ep = match reduce(r, level, 3, -1) {
            Reduced::Done(ep) => ep,
            _ => fail(format!("reduce failed for r={r} at L={level}")),
        };
        if !ep.is_obstr {
            fail(format!("r=2^(L-2)+3={r} not an obstruction at even L={level}"));
        }
        if !is_atomic(r, level, 3, -1).unwrap_or_else(|| fail("overflow (atomic)".into())) {
            fail(format!("r={r} not atomic at L={level}"));
        }
        if ep.j != level - 4 {
            fail(format!("J={} != L-4={} at L={level} r={r}", ep.j, level - 4));
        }
        if shift_index(&ep, 3) != Some(1) {
            fail(format!("shift={:?} != 1 at L={level} r={r}", shift_index(&ep, 3)));
        }
    }
    for level in [7u32, 9, 11] {
        let r = (1i128 << (level - 2)) + 3;
        if is_obstruction(r, level, 3, -1).unwrap_or_else(|| fail("overflow".into())) {
            fail(format!("r=2^(L-2)+3={r} should NOT be an obstruction at odd L={level}"));
        }
    }
    println!("CONFIRM no counterexample: r=2^(L-2)+3 is an atomic obstruction with J=L-4, shift 1 for even L in {{6,8,10,12}}; not an obstruction for odd L in {{7,9,11}} (a=3, b=-1)");
    exit(0);
}
