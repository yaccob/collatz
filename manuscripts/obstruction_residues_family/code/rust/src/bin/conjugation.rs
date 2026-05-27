//! Falsifier for thm_conjugation (\label{thm:conjugation}) and, as its b=-1
//! special case, cor_manuscript_involution (\label{cor:involution}).
//!
//! Psi_b(r) = b*r mod 2^L is a shift-index-preserving bijection
//! O_L^{(a,1)} -> O_L^{(a,b)} (odd b != 0); and the involution r -> 2^L - r
//! equals Psi_{-1}, carrying O_L^{(3,-1)} onto O_L^{(3,+1)}.
//!
//! Contract: prints CONFIRM <domain> / FALSIFY <reason>; exit 0 / 1.

use or_family_falsifiers::{obstructions, shift_index};
use std::collections::HashMap;
use std::process::exit;

fn fail(m: String) -> ! {
    println!("FALSIFY {m}");
    exit(1);
}

/// {r -> shift_index} over the obstructions of T_{a,c} at level L.
fn shift_map(level: u32, a: i128, c: i128) -> HashMap<i128, i64> {
    let obs = obstructions(level, a, c)
        .unwrap_or_else(|_| fail(format!("fixed-width overflow a={a} c={c} L={level}")));
    obs.into_iter()
        .map(|(r, ep)| (r, shift_index(&ep, a).unwrap_or(i64::MIN)))
        .collect()
}

fn main() {
    let cases: [(i128, &[i128], std::ops::Range<u32>); 2] = [
        (3, &[-7, -5, -3, -1, 1, 3, 5, 7, 9, 11, 13], 5..11),
        (7, &[-3, -1, 1, 3, 5], 7..10),
    ];
    for (a, bs, levels) in cases {
        for &b in bs {
            if b == 0 || b % 2 == 0 {
                continue;
            }
            for level in levels.clone() {
                let modulus = 1i128 << level;
                let src = shift_map(level, a, 1);
                let dst = shift_map(level, a, b);
                let mut mapped: HashMap<i128, i64> = HashMap::new();
                for (&r, &s) in &src {
                    mapped.insert((b * r).rem_euclid(modulus), s);
                }
                if mapped.len() != src.len() {
                    fail(format!("Psi_b not injective: a={a} b={b} L={level}"));
                }
                let kmapped: std::collections::HashSet<_> = mapped.keys().copied().collect();
                let kdst: std::collections::HashSet<_> = dst.keys().copied().collect();
                if kmapped != kdst {
                    fail(format!("Psi_b not onto: a={a} b={b} L={level} (|src|={} |dst|={})", src.len(), dst.len()));
                }
                for (rr, s) in &mapped {
                    if dst[rr] != *s {
                        fail(format!("shift not preserved: a={a} b={b} L={level} r'={rr}"));
                    }
                }
            }
        }
    }

    // involution r -> 2^L - r equals Psi_{-1} on O^(3,-1) -> O^(3,+1)
    for level in 5..12u32 {
        let modulus = 1i128 << level;
        let om: std::collections::HashSet<i128> = shift_map(level, 3, -1).into_keys().collect();
        let op: std::collections::HashSet<i128> = shift_map(level, 3, 1).into_keys().collect();
        let inv: std::collections::HashSet<i128> = om.iter().map(|&r| modulus - r).collect();
        if inv != op {
            fail(format!("involution r->2^L-r does not map O^(3,-1) onto O^(3,+1) at L={level}"));
        }
        for &r in &om {
            if modulus - r != (-r).rem_euclid(modulus) {
                fail(format!("2^L-r != Psi_-1(r) at L={level} r={r}"));
            }
        }
    }

    println!("CONFIRM no counterexample: Psi_b bijection+shift over a in {{3,7}} with listed odd b; involution = Psi_-1 for a=3, L=5..11");
    exit(0);
}
