//! Falsifier for fact_empirical_enumeration — the manuscript's concrete
//! enumerated numbers (no claim-label of their own; they live in tables and
//! prose). Re-derives each from unhacked enumeration and refuses any mismatch.
//! Guards exactly the value class where a C(a) rounding slip survived into
//! review 011 undetected.
//!
//! Covered:
//!   tab:order   — multiplicative order e = ord_{|a|}(2);
//!   tab:scaling — |O_16^{(a,-1)}| and the derived C(a)=c_W/4^{-e} (a=3 is the
//!                 abstract's rigorous lower bound c_W >= 7556/65536), and the
//!                 caption's log-linear fit (slope -2.64, intercept 1.91, R^2 0.99);
//!   tab:J-stats — atomic G_{!=0} counts |Atom_L| with J_min, J_max=L-4, mean J (a=3);
//!   tab:Jmax-a  — atomic J_max at L=16 and the footnote's all-obstruction max;
//!   sec:tools   — |O_12^{(3,b)}| = 409 for all odd b (b-universality value);
//!   sec:scaling prose — sparse |O_16| for a in {9,17,21};
//!   sec:Lmin prose — |a|=11 vacuity for L<=16, first obstruction at L=18;
//!   app:err-A3 — the inclusion-refuting witnesses r=29,9,33;
//!   conj:correction — the positive-a restriction motivator: |O_14^(-5,b)|=357
//!                     (b-independent) and C(-5)=357/64>5.5, outside the band.
//!
//! Contract: prints CONFIRM <domain> / FALSIFY <reason>; exit 0 / 1.

use or_family_falsifiers::{is_atomic, is_obstruction, obstructions, ord2};
use std::process::exit;

fn fail(m: String) -> ! {
    println!("FALSIFY {m}");
    exit(1);
}

fn card(level: u32, a: i128, c: i128) -> usize {
    obstructions(level, a, c)
        .unwrap_or_else(|_| fail(format!("fixed-width overflow a={a} c={c} L={level}")))
        .len()
}

fn main() {
    // --- tab:order: multiplicative order e = ord_{|a|}(2) -------------------
    for (a, exp_e) in [
        (3i128, 2u32), (5, 4), (7, 3), (9, 6), (11, 10),
        (13, 12), (15, 4), (17, 8), (31, 5),
    ] {
        let e = ord2(a);
        if e != exp_e {
            fail(format!("tab:order ord_{}(2)={e} != {exp_e}", a.unsigned_abs()));
        }
    }

    // --- tab:scaling: cardinalities at L=16, b=-1, and derived C(a) ---------
    // (a, |O_16| expected, C(a) printed to 2 dp in the manuscript table)
    for (a, exp_card, exp_c) in [
        (3i128, 7556usize, "1.84"),
        (7, 957, "0.93"),
        (15, 159, "0.62"),
        (5, 113, "0.44"),
        (31, 35, "0.55"),
    ] {
        let n = card(16, a, -1);
        if n != exp_card {
            fail(format!("tab:scaling |O_16^({a},-1)|={n} != {exp_card}"));
        }
        let e = ord2(a) as i32;
        let cw = n as f64 / 2f64.powi(16);
        let c_val = cw / 4f64.powi(-e);
        let printed = format!("{c_val:.2}");
        if printed != exp_c {
            fail(format!(
                "tab:scaling C({a})={printed} (cW={cw:.5}, e={e}) != table {exp_c}"
            ));
        }
    }
    // a=3 is the abstract's rigorous lower bound c_W >= 7556/65536.
    if card(16, 3, -1) != 7556 {
        fail("abstract lower bound c_W^(3) != 7556/65536".into());
    }

    // --- tab:J-stats: atomic counts at a=3, b=-1 (even L), J_min/J_max, mean -
    // (L, |Atom_L|, J_min, J_max, mean J to 2 dp ("" = the table's "---")).
    // Atoms are atomic G_{!=0} (no G0 atoms exist), so the mean is over all atoms.
    for (level, exp_atoms, exp_jmin, exp_jmax, exp_jbar) in [
        (10u32, 7usize, 3u32, 6u32, "4.00"),
        (12, 21, 4, 8, "4.76"),
        (14, 66, 4, 10, "5.64"),
        (16, 214, 4, 12, "6.57"),
        (18, 722, 5, 14, ""),
    ] {
        let obs = obstructions(level, 3, -1)
            .unwrap_or_else(|_| fail(format!("overflow a=3 L={level}")));
        let mut atoms = 0usize;
        let (mut jmin, mut jmax, mut jsum) = (u32::MAX, 0u32, 0u64);
        for (r, ep) in &obs {
            if is_atomic(*r, level, 3, -1).unwrap_or_else(|| fail("overflow is_atomic".into())) {
                atoms += 1;
                jmin = jmin.min(ep.j);
                jmax = jmax.max(ep.j);
                jsum += ep.j as u64;
            }
        }
        if atoms != exp_atoms {
            fail(format!("tab:J-stats |Atom_{level}|={atoms} != {exp_atoms}"));
        }
        if jmin != exp_jmin || jmax != exp_jmax {
            fail(format!(
                "tab:J-stats L={level}: (J_min,J_max)=({jmin},{jmax}) != ({exp_jmin},{exp_jmax})"
            ));
        }
        if jmax != level - 4 {
            fail(format!("tab:J-stats J_max={jmax} != L-4={} at L={level}", level - 4));
        }
        if !exp_jbar.is_empty() {
            let jbar = format!("{:.2}", jsum as f64 / atoms as f64);
            if jbar != exp_jbar {
                fail(format!("tab:J-stats L={level}: mean J={jbar} != {exp_jbar}"));
            }
        }
    }

    // --- tab:Jmax-a: atomic G_{!=0} J_max at L=16, plus the caption footnote's
    // max over ALL obstructions (a=5 -> 8, a=7 -> 10). Atomic = atomic G_{!=0}.
    for (a, exp_atomic_jmax, exp_all_jmax) in [(5i128, 6u32, 8u32), (7, 5, 10)] {
        let obs = obstructions(16, a, -1).unwrap_or_else(|_| fail(format!("overflow a={a} L=16")));
        let (mut atomic_jmax, mut all_jmax) = (0u32, 0u32);
        for (r, ep) in &obs {
            all_jmax = all_jmax.max(ep.j);
            if is_atomic(*r, 16, a, -1).unwrap_or_else(|| fail("overflow is_atomic".into())) {
                atomic_jmax = atomic_jmax.max(ep.j);
            }
        }
        if atomic_jmax != exp_atomic_jmax {
            fail(format!("tab:Jmax-a atomic J_max({a})={atomic_jmax} != {exp_atomic_jmax}"));
        }
        if all_jmax != exp_all_jmax {
            fail(format!("tab:Jmax-a all-obs J_max({a})={all_jmax} != {exp_all_jmax}"));
        }
    }

    // --- sec:tools numeric: |O_12^{(3,b)}| = 409 for all odd b (b-universality)
    for b in [-7i128, -5, -3, -1, 1, 3, 5, 7, 9, 11, 13] {
        let n = card(12, 3, b);
        if n != 409 {
            fail(format!("|O_12^(3,{b})|={n} != 409 (b-universality)"));
        }
    }

    // --- tab:scaling caption: log-linear fit log2(c_W) = m*e + b, with R^2 ---
    // Re-derive from the (already-asserted) L=16 cardinalities; the manuscript
    // prints m=-2.64, b=1.91, R^2=0.99 (all to 2 dp).
    let pts: Vec<(f64, f64)> = [(3i128, 7556usize), (7, 957), (15, 159), (5, 113), (31, 35)]
        .iter()
        .map(|&(a, n)| (ord2(a) as f64, (n as f64 / 2f64.powi(16)).log2()))
        .collect();
    let np = pts.len() as f64;
    let sx: f64 = pts.iter().map(|p| p.0).sum();
    let sy: f64 = pts.iter().map(|p| p.1).sum();
    let sxx: f64 = pts.iter().map(|p| p.0 * p.0).sum();
    let sxy: f64 = pts.iter().map(|p| p.0 * p.1).sum();
    let m = (np * sxy - sx * sy) / (np * sxx - sx * sx);
    let b = (sy - m * sx) / np;
    let ybar = sy / np;
    let sstot: f64 = pts.iter().map(|p| (p.1 - ybar).powi(2)).sum();
    let ssres: f64 = pts.iter().map(|p| (p.1 - (m * p.0 + b)).powi(2)).sum();
    let r2 = 1.0 - ssres / sstot;
    for (got, want, name) in [
        (format!("{m:.2}"), "-2.64", "slope"),
        (format!("{b:.2}"), "1.91", "intercept"),
        (format!("{r2:.2}"), "0.99", "R^2"),
    ] {
        if got != want {
            fail(format!("tab:scaling fit {name}={got} != {want}"));
        }
    }

    // --- sec:scaling prose: sparse |O_16| for under-resolved multipliers -----
    for (a, exp) in [(9i128, 47usize), (17, 1), (21, 69)] {
        let n = card(16, a, -1);
        if n != exp {
            fail(format!("sparse |O_16^({a},-1)|={n} != {exp}"));
        }
    }

    // --- sec:Lmin prose: |a|=11 vacuity up to L<=16, first obstruction at L=18
    for level in 4..=16u32 {
        if card(level, 11, -1) != 0 {
            fail(format!("|O_{level}^(11,-1)| != 0 (claimed vacuous for L<=16)"));
        }
    }
    if card(18, 11, -1) == 0 {
        fail("|O_18^(11,-1)| = 0 (claimed first obstruction at L=18)".into());
    }

    // --- app:err-A3: inclusion-refuting witnesses r in O^{(+q)} \ O^{(-q)} ---
    // (r, L, q): obstruction for +q, not for -q. These hold for the b=+1
    // representatives; at b=-1 the roles reverse (the residues are b-specific,
    // unlike the b-independent cardinalities), so the comparison is fixed at
    // b=+1, matching the appendix witnesses.
    for (r, level, q) in [(29i128, 10u32, 3i128), (9, 10, 7), (33, 12, 31)] {
        let pos = is_obstruction(r, level, q, 1).unwrap_or_else(|| fail("overflow +q".into()));
        let neg = is_obstruction(r, level, -q, 1).unwrap_or_else(|| fail("overflow -q".into()));
        if !pos || neg {
            fail(format!(
                "A3 witness r={r} at L={level}: in O^(+{q})={pos}, in O^(-{q})={neg} (want true,false)"
            ));
        }
    }

    // --- sec:scaling, conj:correction motivation: the positive-a restriction --
    // The conjecture's restriction to positive a is justified by the smallest
    // negative non-Mersenne multiplier a=-5 (e=4) leaving the positive-a band:
    // the b-independent cardinality |O_14^(-5,b)| = 357 gives the rigorous lower
    // bound C(-5) >= 357/64 > 5.5, far outside the [0.44,1.84] of tab:scaling.
    for c in [1i128, -1] {
        let n = card(14, -5, c);
        if n != 357 {
            fail(format!("conj:correction |O_14^(-5,{c})|={n} != 357"));
        }
    }
    // C(-5) >= (357/2^14)/4^{-e} with e=4 equals 357/64 = 5.578...
    {
        let e = ord2(-5) as i32; // = 4
        let c_m5 = (357f64 / 2f64.powi(14)) / 4f64.powi(-e);
        if !(c_m5 > 5.5) {
            fail(format!("conj:correction C(-5)={c_m5:.4} not > 5.5"));
        }
        if !(c_m5 > 1.84) {
            fail(format!("conj:correction C(-5)={c_m5:.4} not outside positive-a band [..,1.84]"));
        }
    }

    // --- rem:deep-scaling: deeper rigorous lower bounds (L=24), band, alpha<2 -
    // The remark cites C(3)=2.15 at L=24 (up from 1.84 at L=16), the lower-bound
    // band [0.56,4.40] over the eight multipliers, and fitted atomic growth
    // alpha(a) in [1.46,1.88] (all < 2) for the well-resolved a <= 15.
    // Atom counts use |Atom_l| = |O_l| - 2|O_{l-1}| (lift balance; no G0 atoms).
    let well = [3i128, 5, 7, 9, 15];
    let mut alpha_min = f64::INFINITY;
    let mut alpha_max = 0f64;
    for a in well {
        let o: Vec<f64> = (16..=24u32).map(|l| card(l, a, -1) as f64).collect();
        // log-linear fit of a_l = |O_l| - 2|O_{l-1}| over l = 18..=24.
        let pts: Vec<(f64, f64)> = (18..=24u32)
            .map(|l| {
                let i = (l - 16) as usize;
                (l as f64, (o[i] - 2.0 * o[i - 1]).ln())
            })
            .collect();
        let np = pts.len() as f64;
        let sx: f64 = pts.iter().map(|p| p.0).sum();
        let sy: f64 = pts.iter().map(|p| p.1).sum();
        let sxx: f64 = pts.iter().map(|p| p.0 * p.0).sum();
        let sxy: f64 = pts.iter().map(|p| p.0 * p.1).sum();
        let alpha = ((np * sxy - sx * sy) / (np * sxx - sx * sx)).exp();
        if !(alpha < 2.0) {
            fail(format!("rem:deep-scaling alpha({a})={alpha:.4} not < 2"));
        }
        alpha_min = alpha_min.min(alpha);
        alpha_max = alpha_max.max(alpha);
    }
    if format!("{alpha_min:.2}") != "1.46" || format!("{alpha_max:.2}") != "1.88" {
        fail(format!(
            "rem:deep-scaling alpha band [{alpha_min:.2},{alpha_max:.2}] != [1.46,1.88]"
        ));
    }
    // Exact |O_24| for all eight: guards the deeper lower bounds, C(3)=2.15,
    // and the band extremes (min a=31 -> 0.56, max a=21 -> 4.40).
    let exp24: [(i128, usize); 8] = [
        (3, 2251983), (5, 48942), (7, 265409), (9, 14822),
        (15, 41899), (17, 453), (21, 18002), (31, 9193),
    ];
    let (mut cmin, mut cmax) = (f64::INFINITY, 0f64);
    for (a, exp) in exp24 {
        let n = card(24, a, -1);
        if n != exp {
            fail(format!("rem:deep-scaling |O_24^({a},-1)|={n} != {exp}"));
        }
        let e = ord2(a) as i32;
        let c_val = (n as f64 / 2f64.powi(24)) / 4f64.powi(-e);
        cmin = cmin.min(c_val);
        cmax = cmax.max(c_val);
        if a == 3 && format!("{c_val:.2}") != "2.15" {
            fail(format!("rem:deep-scaling C(3) at L=24 = {c_val:.2} != 2.15"));
        }
    }
    if format!("{cmin:.2}") != "0.56" || format!("{cmax:.2}") != "4.40" {
        fail(format!(
            "rem:deep-scaling C-band at L=24 [{cmin:.2},{cmax:.2}] != [0.56,4.40]"
        ));
    }

    println!(
        "CONFIRM no counterexample: tab:order e-values, tab:scaling cardinalities+C(a) \
         (a in {{3,5,7,15,31}}, 7556=abstract bound) + fit (-2.64,1.91,R^2 0.99), \
         tab:J-stats atom counts 7/21/66/214/722 with J_max=L-4 and means 4.00/4.76/5.64/6.57 \
         (a=3, L=10..18), tab:Jmax-a atomic 6/5 + all-obs 8/10 (a=5,7), |O_12^(3,b)|=409, \
         sparse |O_16| 47/1/69 (a=9,17,21), |a|=11 vacuous L<=16 & nonempty at L=18, \
         A3 witnesses r=29/9/33 in O^(+q)\\O^(-q), \
         conj:correction |O_14^(-5,b)|=357 & C(-5)=357/64>5.5 (outside band), \
         rem:deep-scaling L=24 lower bounds (|O_24| 8 multipliers, C(3)=2.15, \
         band [0.56,4.40]) + fitted alpha(a) in [1.46,1.88] (all <2, a<=15)"
    );
    exit(0);
}
