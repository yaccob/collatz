//! Shared parallel-reduction core for the obstruction_residues_family Rust
//! falsifiers — the fixed-width counterpart of checks/_reduction.py.
//!
//! T_{a,c}(n) = (a n + c)/2^{v_2(a n + c)}. An obstruction residue r at level
//! L reduces in J steps to a terminal datum; the shift index is
//! delta_J = V_K - V_I - v, and (order lemma) e = ord_{|a|}(2) divides it.
//!
//! All arithmetic is fixed-width i128 with EXPLICIT checked overflow: an
//! out-of-range case is surfaced as `Reduced::Overflow`, never silently
//! wrapped (a silent overflow in a falsifier manufactures false confidence).
//! The obstruction test avoids rationals via the integer recurrence
//! D_0 = c, D_{j+1} = a D_j - c X_j  (X_j = 2^{V_K^{(j)}} - 2^{V_I^{(j)}+v}):
//! r is an obstruction iff a D_J - c X_J = 0 at termination.

use rayon::prelude::*;

#[inline]
pub fn v2(n: i128) -> u32 {
    debug_assert!(n != 0);
    n.unsigned_abs().trailing_zeros()
}

/// Multiplicative order e = ord_{|a|}(2) (a odd; 1 for |a| = 1).
pub fn ord2(a: i128) -> u32 {
    let a = a.unsigned_abs();
    if a == 1 {
        return 1;
    }
    let (mut k, mut x) = (1u32, 2u128 % a);
    while x != 1 {
        x = (x * 2) % a;
        k += 1;
    }
    k
}

/// a*x + c, or None on i128 overflow.
#[inline]
pub fn fma(a: i128, x: i128, c: i128) -> Option<i128> {
    a.checked_mul(x)?.checked_add(c)
}

/// 1 << k as i128, or None if k leaves the positive range.
#[inline]
pub fn pow2(k: u32) -> Option<i128> {
    if k >= 127 {
        None
    } else {
        Some(1i128 << k)
    }
}

#[derive(Clone, Copy)]
pub struct Endpoint {
    pub is_obstr: bool,
    pub j: u32,   // termination index
    pub v_k: u32, // V_K^{(J)}
    pub v_i: u32, // V_I^{(J)}
    pub v: u32,   // initial v_2(r + c)
}

pub enum Reduced {
    Ineligible,
    Overflow,
    Done(Endpoint),
}

/// Parallel reduction of residue r at level L for T_{a,c}.
pub fn reduce(r: i128, level: u32, a: i128, c: i128) -> Reduced {
    macro_rules! ovf {
        ($e:expr) => {
            match $e {
                Some(x) => x,
                None => return Reduced::Overflow,
            }
        };
    }
    if r & 1 == 0 || c == 0 || c & 1 == 0 || a & 1 == 0 {
        return Reduced::Ineligible;
    }
    let s = r + c;
    if s == 0 {
        return Reduced::Ineligible;
    }
    let v = v2(s);
    if v == 0 || v >= level {
        return Reduced::Ineligible;
    }
    let mut a_k = r;
    let mut a_i = s >> v;
    let mut vk_cum = 0u32;
    let mut vi_cum = 0u32;
    let mut d = c; // D_0
    let mut j = 0u32;
    loop {
        let ak = ovf!(fma(a, a_k, c));
        let ai = ovf!(fma(a, a_i, c));
        let vk = v2(ak);
        let vi = v2(ai);
        let res_k = level - vk_cum; // v2(b_K)
        let res_i = (level - v) - vi_cum; // v2(b_I)
        if vk >= res_k || vi >= res_i {
            let x_j = ovf!(pow2(vk_cum)) - ovf!(pow2(vi_cum + v));
            let lhs = ovf!(ovf!(a.checked_mul(d)).checked_sub(ovf!(c.checked_mul(x_j))));
            return Reduced::Done(Endpoint {
                is_obstr: lhs == 0,
                j,
                v_k: vk_cum,
                v_i: vi_cum,
                v,
            });
        }
        let x = ovf!(pow2(vk_cum)) - ovf!(pow2(vi_cum + v));
        d = ovf!(ovf!(a.checked_mul(d)).checked_sub(ovf!(c.checked_mul(x))));
        a_k = ak >> vk;
        a_i = ai >> vi;
        vk_cum += vk;
        vi_cum += vi;
        j += 1;
    }
}

pub enum Traced {
    Ineligible,
    Overflow,
    Done { snaps: Vec<(u32, u32)>, v: u32 },
}

/// Cumulative valuation trace: snaps[j] = (V_K^{(j)}, V_I^{(j)}) for j=0..J
/// (snaps[0] = (0,0)). Used by the diophantine-identity check.
pub fn cumulative_trace(r: i128, level: u32, a: i128, c: i128) -> Traced {
    macro_rules! ovf {
        ($e:expr) => {
            match $e {
                Some(x) => x,
                None => return Traced::Overflow,
            }
        };
    }
    if r & 1 == 0 || c == 0 || c & 1 == 0 || a & 1 == 0 {
        return Traced::Ineligible;
    }
    let s = r + c;
    if s == 0 {
        return Traced::Ineligible;
    }
    let v = v2(s);
    if v == 0 || v >= level {
        return Traced::Ineligible;
    }
    let mut a_k = r;
    let mut a_i = s >> v;
    let mut vk_cum = 0u32;
    let mut vi_cum = 0u32;
    let mut snaps = vec![(0u32, 0u32)];
    loop {
        let ak = ovf!(fma(a, a_k, c));
        let ai = ovf!(fma(a, a_i, c));
        let vk = v2(ak);
        let vi = v2(ai);
        if vk >= level - vk_cum || vi >= (level - v) - vi_cum {
            return Traced::Done { snaps, v };
        }
        a_k = ak >> vk;
        a_i = ai >> vi;
        vk_cum += vk;
        vi_cum += vi;
        snaps.push((vk_cum, vi_cum));
    }
}

/// delta_J / e, or None if e does not divide delta_J (order-lemma violation).
pub fn shift_index(ep: &Endpoint, a: i128) -> Option<i64> {
    let delta = ep.v_k as i64 - ep.v_i as i64 - ep.v as i64;
    let e = ord2(a) as i64;
    if delta.rem_euclid(e) != 0 {
        None
    } else {
        Some(delta / e)
    }
}

/// Is r an obstruction at level L? None on overflow.
pub fn is_obstruction(r: i128, level: u32, a: i128, c: i128) -> Option<bool> {
    match reduce(r, level, a, c) {
        Reduced::Done(ep) => Some(ep.is_obstr),
        Reduced::Ineligible => Some(false),
        Reduced::Overflow => None,
    }
}

/// r in O_L is atomic iff r mod 2^{L-1} is not in O_{L-1}. None on overflow.
pub fn is_atomic(r: i128, level: u32, a: i128, c: i128) -> Option<bool> {
    if level <= 1 {
        return Some(true);
    }
    let proj = r % (1i128 << (level - 1));
    Some(!is_obstruction(proj, level - 1, a, c)?)
}

/// All (r, endpoint) obstructions at level L. Err(()) if any residue overflows.
pub fn obstructions(level: u32, a: i128, c: i128) -> Result<Vec<(i128, Endpoint)>, ()> {
    let parts: Vec<Result<Option<(i128, Endpoint)>, ()>> = (0..(1u128 << (level - 1)))
        .into_par_iter()
        .map(|i| {
            let r = (2 * i + 1) as i128;
            match reduce(r, level, a, c) {
                Reduced::Done(ep) => Ok(if ep.is_obstr { Some((r, ep)) } else { None }),
                Reduced::Ineligible => Ok(None),
                Reduced::Overflow => Err(()),
            }
        })
        .collect();
    let mut out = Vec::new();
    for p in parts {
        match p {
            Ok(Some(x)) => out.push(x),
            Ok(None) => {}
            Err(()) => return Err(()),
        }
    }
    Ok(out)
}
