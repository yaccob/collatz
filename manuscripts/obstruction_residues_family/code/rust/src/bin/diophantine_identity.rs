//! Falsifier for thm_diophantine_identity (\label{thm:diophantine}).
//!
//! For every obstruction residue r at level L with termination index J,
//!   a^{J+1} = sum_{j=0}^{J} a^{J-j} X_j,  X_j = 2^{V_K^{(j)}} - 2^{V_I^{(j)}+v},
//! with (V_K^{(j)}, V_I^{(j)}) from the reduction trace (V^{(0)}=(0,0)).
//!
//! Contract: prints CONFIRM <domain> / FALSIFY <reason>; exit 0 / 1.

use or_family_falsifiers::{cumulative_trace, obstructions, pow2, Traced};
use std::process::exit;

fn fail(m: String) -> ! {
    println!("FALSIFY {m}");
    exit(1);
}

/// a^n with checked overflow.
fn checked_pow(a: i128, n: u32) -> Option<i128> {
    let mut acc = 1i128;
    for _ in 0..n {
        acc = acc.checked_mul(a)?;
    }
    Some(acc)
}

fn main() {
    let mut tested = 0u64;
    for a in [3i128, 5, 7, -1, -3] {
        for c in [1i128, -1] {
            for level in 4..12u32 {
                let obs = obstructions(level, a, c)
                    .unwrap_or_else(|_| fail(format!("overflow (obstructions) a={a} c={c} L={level}")));
                for (r, ep) in obs {
                    let (snaps, v) = match cumulative_trace(r, level, a, c) {
                        Traced::Done { snaps, v } => (snaps, v),
                        Traced::Overflow => fail(format!("overflow (trace) a={a} c={c} L={level} r={r}")),
                        Traced::Ineligible => fail(format!("trace ineligible for obstruction a={a} c={c} L={level} r={r}")),
                    };
                    let j = ep.j;
                    if snaps.len() as u32 != j + 1 {
                        fail(format!("trace length {} != J+1={} (a={a} c={c} L={level} r={r})", snaps.len(), j + 1));
                    }
                    let lhs = checked_pow(a, j + 1)
                        .unwrap_or_else(|| fail(format!("overflow a^(J+1) a={a} L={level} r={r}")));
                    let mut rhs = 0i128;
                    for (jj, &(vk, vi)) in snaps.iter().enumerate() {
                        let x_j = pow2(vk).unwrap() - pow2(vi + v).unwrap();
                        let term = checked_pow(a, j - jj as u32)
                            .unwrap_or_else(|| fail(format!("overflow a^(J-j) a={a} L={level} r={r}")))
                            .checked_mul(x_j)
                            .unwrap_or_else(|| fail(format!("overflow term a={a} L={level} r={r}")));
                        rhs = rhs.checked_add(term)
                            .unwrap_or_else(|| fail(format!("overflow sum a={a} L={level} r={r}")));
                    }
                    tested += 1;
                    if lhs != rhs {
                        fail(format!("identity fails: a={a} c={c} L={level} r={r} a^(J+1)={lhs} != sum={rhs}"));
                    }
                }
            }
        }
    }
    if tested == 0 {
        fail("vacuous: no obstructions enumerated".into());
    }
    println!("CONFIRM no counterexample: diophantine identity holds on {tested} obstructions (a in {{3,5,7,-1,-3}}, c in {{1,-1}}, L=4..11)");
    exit(0);
}
