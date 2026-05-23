//! High-performance enumeration of |Obs_L| for the obstruction-residues
//! manuscript. Mirrors the algorithm of count_obstructions.py but uses
//! dyadic rationals (i128 numerator + i32 exponent) instead of arbitrary
//! Fractions, and rayon for parallel enumeration over odd r in [1, 2^L].
//!
//! Termination criterion: r is an obstruction iff the parallel two-track
//! T_- reduction terminates with X_end := 3 d_J + c_J = 1.

use rayon::prelude::*;
use std::env;
use std::time::Instant;

/// Dyadic rational: value = num * 2^exp.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct Dyadic {
    num: i128,
    exp: i32,
}

impl Dyadic {
    const ZERO: Self = Self { num: 0, exp: 0 };

    #[inline]
    fn normalized(self) -> Self {
        if self.num == 0 {
            return Self::ZERO;
        }
        let tz = self.num.trailing_zeros() as i32;
        Self {
            num: self.num >> tz,
            exp: self.exp + tz,
        }
    }

    #[inline]
    fn add(self, other: Self) -> Self {
        if self.num == 0 {
            return other;
        }
        if other.num == 0 {
            return self;
        }
        let (lo, hi) = if self.exp <= other.exp {
            (self, other)
        } else {
            (other, self)
        };
        let shift = (hi.exp - lo.exp) as u32;
        debug_assert!(shift < 120, "exponent gap too large: {}", shift);
        Self {
            num: lo.num + (hi.num << shift),
            exp: lo.exp,
        }
        .normalized()
    }

    #[inline]
    fn is_one(&self) -> bool {
        self.num == 1 && self.exp == 0
    }
}

/// Decide whether r is an obstruction at level L.
#[inline]
fn is_obstruction(r: u64, l: u32) -> bool {
    if r & 1 == 0 || r == 1 {
        return false;
    }
    let v = (r - 1).trailing_zeros();
    if v == 0 || v >= l {
        return false;
    }

    // K-track: (a_K, b_K) = (r, 2^L); we track only a_K and the cumulative
    // valuation V_K via v_acc_k so that the residual modulus is L - v_acc_k.
    // I-track analogous, with initial modulus exponent L - v.
    let mut a_k: u128 = r as u128;
    let mut a_i: u128 = ((r - 1) >> v) as u128;
    let mut v_acc_k: u32 = 0;
    let mut v_acc_i: u32 = 0;

    // c is always a pure power of 2; track only the exponent.
    // d is a general dyadic.
    let mut c_exp: i32 = -(v as i32);
    let mut d = Dyadic {
        num: -1,
        exp: -(v as i32),
    };

    loop {
        let three_a_k = 3 * a_k - 1;
        let v_k = three_a_k.trailing_zeros();
        let three_a_i = 3 * a_i - 1;
        let v_i = three_a_i.trailing_zeros();
        let avail_k = l - v_acc_k;
        let avail_i = l - v - v_acc_i;

        if v_k >= avail_k || v_i >= avail_i {
            // Terminate: check X_end = 3 d_J + c_J = 1.
            let c = Dyadic {
                num: 1,
                exp: c_exp,
            };
            let three_d = Dyadic {
                num: 3 * d.num,
                exp: d.exp,
            };
            return three_d.add(c).is_one();
        }

        // c_{j+1} = c_j * 2^{v_K - v_I}
        let new_c_exp = c_exp + v_k as i32 - v_i as i32;
        // d_{j+1} = (3 d_j + c_j - 1) / 2^{v_I}
        let three_d = Dyadic {
            num: 3 * d.num,
            exp: d.exp,
        };
        let c_dy = Dyadic {
            num: 1,
            exp: c_exp,
        };
        let m_one = Dyadic { num: -1, exp: 0 };
        let mut new_d = three_d.add(c_dy).add(m_one);
        new_d.exp -= v_i as i32;
        // already normalized by add(), but exp shift may leave it normalized too

        c_exp = new_c_exp;
        d = new_d;
        a_k = three_a_k >> v_k;
        a_i = three_a_i >> v_i;
        v_acc_k += v_k;
        v_acc_i += v_i;
    }
}

/// |Obs_L|: count odd r in {1, ..., 2^L} with X_end(r, L) = 1.
fn count(l: u32) -> u64 {
    assert!(l >= 1 && l <= 63, "L must be in 1..=63");
    let half = 1u64 << (l - 1);
    (0u64..half)
        .into_par_iter()
        .filter(|&k| is_obstruction(2 * k + 1, l))
        .count() as u64
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: {} L_start [L_end]", args[0]);
        eprintln!();
        eprintln!("  Enumerates |Obs_L| (and the resulting lower bound");
        eprintln!("  c_W >= |Obs_L|/2^L) for L in [L_start, L_end].");
        std::process::exit(1);
    }
    let l_start: u32 = args[1].parse().expect("L_start must be int");
    let l_end: u32 = args
        .get(2)
        .and_then(|s| s.parse().ok())
        .unwrap_or(l_start);
    assert!(l_start <= l_end, "L_start must be <= L_end");

    let n_threads = rayon::current_num_threads();
    eprintln!("# rayon threads: {}", n_threads);
    println!(
        "# {:>3} {:>16} {:>14} {:>20} {:>12}",
        "L", "|Obs_L|", "ratio", "= |Obs_L| / 2^L", "wall_sec"
    );

    let mut prev: Option<u64> = None;
    for l in l_start..=l_end {
        let start = Instant::now();
        let n = count(l);
        let elapsed = start.elapsed().as_secs_f64();
        let denom: u128 = 1u128 << l;
        let ratio = n as f64 / denom as f64;
        let lift_ok = match prev {
            Some(p) => {
                let diff = n as i64 - 2 * p as i64;
                if diff >= 0 {
                    format!("  lift_ok atoms={}", diff)
                } else {
                    format!("  LIFT_VIOLATED diff={}", diff)
                }
            }
            None => String::new(),
        };
        println!(
            "  {:>3} {:>16} {:>14.8} ({:>10} / 2^{:<2}) {:>12.3}{}",
            l, n, ratio, n, l, elapsed, lift_ok
        );
        prev = Some(n);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Reference values from Table tab:appendix-counts (obstruction_residues.tex).
    const KNOWN: &[(u32, u64)] = &[
        (5, 1),
        (6, 3),
        (7, 8),
        (8, 19),
        (9, 42),
        (10, 91),
        (11, 194),
        (12, 409),
        (13, 855),
        (14, 1776),
        (15, 3671),
        (16, 7556),
    ];

    #[test]
    fn matches_manuscript_table() {
        for &(l, expected) in KNOWN {
            let got = count(l);
            assert_eq!(got, expected, "L={}: got {}, expected {}", l, got, expected);
        }
    }

    #[test]
    fn lift_balance_holds() {
        // |Obs_L| >= 2|Obs_{L-1}|; difference = |Atom_L^{G_ne0}|.
        let mut prev = count(5);
        for l in 6u32..=14 {
            let n = count(l);
            assert!(
                n >= 2 * prev,
                "L={}: lift balance violated (n={}, 2*prev={})",
                l,
                n,
                2 * prev
            );
            prev = n;
        }
    }
}
