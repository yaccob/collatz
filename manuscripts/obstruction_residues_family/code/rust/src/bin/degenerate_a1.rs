//! Falsifier for thm_degenerate_a1 (\label{thm:edge-case}).
//!
//! |a| = 1 edge cases:
//!   a = +1, any odd b: O_L^{(1,b)} empty for every L;
//!   a = -1, b = +1: |O_L^{(-1,1)}| = 2^{L-2}, residues exactly r = 1 (mod 4);
//!   a = -1, b in {-1,3}: |O_L^{(-1,b)}| = 2^{L-2}.
//! Together: the obstruction theory needs |a| >= 3 intrinsically.
//!
//! Contract: prints CONFIRM <domain> / FALSIFY <reason>; exit 0 / 1.

use or_family_falsifiers::obstructions;
use std::process::exit;

fn fail(m: String) -> ! {
    println!("FALSIFY {m}");
    exit(1);
}

fn obs(level: u32, a: i128, c: i128) -> Vec<i128> {
    obstructions(level, a, c)
        .unwrap_or_else(|_| fail(format!("fixed-width overflow a={a} c={c} L={level}")))
        .into_iter()
        .map(|(r, _)| r)
        .collect()
}

fn main() {
    for b in [1i128, -1, 3, 5] {
        for level in 3..12u32 {
            let o = obs(level, 1, b);
            if !o.is_empty() {
                let head: Vec<i128> = o.iter().take(5).copied().collect();
                fail(format!("a=+1 not empty: b={b} L={level} O={head:?}"));
            }
        }
    }
    for level in 3..11u32 {
        let o = obs(level, -1, 1);
        if o.len() != 1usize << (level - 2) {
            fail(format!("a=-1,b=1 count {} != 2^(L-2)={} at L={level}", o.len(), 1usize << (level - 2)));
        }
        if o.iter().any(|&r| r % 4 != 1) {
            fail(format!("a=-1,b=1 residues not all =1 mod 4 at L={level}"));
        }
    }
    for b in [-1i128, 3] {
        for level in 3..11u32 {
            if obs(level, -1, b).len() != 1usize << (level - 2) {
                fail(format!("a=-1 count != 2^(L-2): b={b} L={level}"));
            }
        }
    }
    println!("CONFIRM no counterexample: a=+1 empty (b in {{1,-1,3,5}}, L=3..11); a=-1 gives 2^(L-2) (r=1 mod 4 for b=1), L=3..10");
    exit(0);
}
