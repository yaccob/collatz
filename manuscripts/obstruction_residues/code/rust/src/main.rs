//! High-performance enumeration of |Obs_L| for the obstruction-residues
//! manuscript. Mirrors the algorithm of count_obstructions.py but uses
//! dyadic rationals (i128 numerator + i32 exponent) instead of arbitrary
//! Fractions, and rayon for parallel enumeration over odd r in [1, 2^L].
//!
//! Termination criterion: r is an obstruction iff the parallel two-track
//! T_- reduction terminates with X_end := 3 d_J + c_J = 1.
//!
//! Within each level L, work is split into chunks of 2^chunk_bits odd r
//! each, processed sequentially with internal rayon parallelism. After
//! each chunk, a TSV line is appended to the runlog so that interrupted
//! runs can be resumed via --resume.

use rayon::prelude::*;
use std::collections::HashMap;
use std::env;
use std::fs::{File, OpenOptions};
use std::io::{BufRead, BufReader, Write};
use std::path::{Path, PathBuf};
use std::time::{Instant, SystemTime, UNIX_EPOCH};

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

/// Decide whether r is an obstruction at level L; if so, return the shift index a.
///
/// At termination the parameter c equals 2^{c_exp}. For an obstruction with shift
/// index a, the parity lemma forces c = 4^a, i.e. c_exp = 2a. We return Some(a)
/// when 3 d_J + c_J = 1 (the X-invariant condition) and c_exp is even; None
/// otherwise. The c_exp parity check is defensive — the parity lemma rules out
/// odd c_exp for obstructions, but we don't want to silently miscount if a
/// future code change broke that invariant.
#[inline]
fn obstruction_shift(r: u64, l: u32) -> Option<i32> {
    if r & 1 == 0 || r == 1 {
        return None;
    }
    let v = (r - 1).trailing_zeros();
    if v == 0 || v >= l {
        return None;
    }

    let mut a_k: u128 = r as u128;
    let mut a_i: u128 = ((r - 1) >> v) as u128;
    let mut v_acc_k: u32 = 0;
    let mut v_acc_i: u32 = 0;
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
            let c = Dyadic {
                num: 1,
                exp: c_exp,
            };
            let three_d = Dyadic {
                num: 3 * d.num,
                exp: d.exp,
            };
            if three_d.add(c).is_one() {
                if c_exp.rem_euclid(2) == 0 {
                    return Some(c_exp / 2);
                } else {
                    // parity lemma violation — should never happen for an obstruction
                    return None;
                }
            } else {
                return None;
            }
        }

        let new_c_exp = c_exp + v_k as i32 - v_i as i32;
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

        c_exp = new_c_exp;
        d = new_d;
        a_k = three_a_k >> v_k;
        a_i = three_a_i >> v_i;
        v_acc_k += v_k;
        v_acc_i += v_i;
    }
}

/// Boolean wrapper for callers that don't need the shift index.
/// Currently only used by the test module; kept as a named entry point so
/// callers can opt out of the HashMap overhead in the future.
#[cfg(test)]
#[inline]
fn is_obstruction(r: u64, l: u32) -> bool {
    obstruction_shift(r, l).is_some()
}

/// Count obstructions for odd r corresponding to k in [k_start, k_end)
/// (i.e. r = 2*k + 1), bucketed by shift index. Total count is the sum of
/// the returned map's values.
fn count_chunk_shifts(l: u32, k_start: u64, k_end: u64) -> HashMap<i32, u64> {
    (k_start..k_end)
        .into_par_iter()
        .fold(
            HashMap::<i32, u64>::new,
            |mut acc, k| {
                if let Some(a) = obstruction_shift(2 * k + 1, l) {
                    *acc.entry(a).or_insert(0) += 1;
                }
                acc
            },
        )
        .reduce(HashMap::<i32, u64>::new, |mut a, b| {
            for (k, v) in b {
                *a.entry(k).or_insert(0) += v;
            }
            a
        })
}

/// Total count for the chunk (sum of shift buckets). Used only in tests; main
/// path goes through count_chunk_shifts directly.
#[cfg(test)]
fn count_chunk(l: u32, k_start: u64, k_end: u64) -> u64 {
    count_chunk_shifts(l, k_start, k_end).values().sum()
}

/// Full level count (no checkpointing). Kept for tests.
#[cfg(test)]
fn count(l: u32) -> u64 {
    assert!((1..=63).contains(&l), "L must be in 1..=63");
    let half = 1u64 << (l - 1);
    count_chunk(l, 0, half)
}

// -------- checkpoint / runlog --------

#[derive(Default, Debug)]
struct LevelState {
    /// chunk_idx -> count (for chunks completed in prior runs)
    done_chunks: HashMap<u64, u64>,
    /// chunk_bits used in prior runs at this level (must match on resume)
    chunk_bits_seen: Option<u32>,
    /// True if a `level` line has been written: skip entirely
    level_done: bool,
    level_total: u64,
    /// Per-shift count accumulated across chunks completed in prior runs.
    /// Populated from chunk_shift rows in --stats-output when resuming.
    /// Empty if no stats-output was used previously.
    done_shifts: HashMap<i32, u64>,
}

fn read_runlog(path: &Path) -> HashMap<u32, LevelState> {
    let mut state: HashMap<u32, LevelState> = HashMap::new();
    let file = match File::open(path) {
        Ok(f) => f,
        Err(_) => return state,
    };
    for line in BufReader::new(file).lines().map_while(Result::ok) {
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        let cols: Vec<&str> = line.split('\t').collect();
        if cols.len() < 2 {
            continue;
        }
        let kind = cols[0];
        let l: u32 = match cols[1].parse() {
            Ok(v) => v,
            Err(_) => continue,
        };
        let entry = state.entry(l).or_default();
        match kind {
            // chunk\tL\tci\tchunk_size\tk_start\tk_end\tcount\twall_sec\tts_epoch
            "chunk" if cols.len() >= 9 => {
                let ci: u64 = cols[2].parse().unwrap_or(u64::MAX);
                let chunk_size: u64 = cols[3].parse().unwrap_or(0);
                let count: u64 = cols[6].parse().unwrap_or(0);
                if ci != u64::MAX {
                    entry.done_chunks.insert(ci, count);
                    let bits = chunk_size.trailing_zeros();
                    entry.chunk_bits_seen.get_or_insert(bits);
                }
            }
            // level\tL\t-\t-\t-\t-\ttotal\twall_sec\tts_epoch
            "level" if cols.len() >= 9 => {
                entry.level_done = true;
                entry.level_total = cols[6].parse().unwrap_or(0);
            }
            _ => {}
        }
    }
    state
}

/// Read chunk_shift rows from the stats output and accumulate per-level
/// shift sums into `state`. Must be called *after* `read_runlog` so that the
/// LevelState entries exist (and so we can tell which chunks have already
/// been counted as "done" via the matching runlog rows). Idempotent in the
/// face of additional level_shift rows already present — we ignore those and
/// recompute from chunk_shift, which is the authoritative per-chunk data.
fn read_stats(path: &Path, state: &mut HashMap<u32, LevelState>) {
    let file = match File::open(path) {
        Ok(f) => f,
        Err(_) => return,
    };
    for line in BufReader::new(file).lines().map_while(Result::ok) {
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        let cols: Vec<&str> = line.split('\t').collect();
        if cols.len() < 8 {
            continue;
        }
        if cols[0] != "chunk_shift" {
            continue;
        }
        let l: u32 = match cols[1].parse() {
            Ok(v) => v,
            Err(_) => continue,
        };
        let ci: u64 = cols[2].parse().unwrap_or(u64::MAX);
        let a: i32 = match cols[6].parse() {
            Ok(v) => v,
            Err(_) => continue,
        };
        let cnt: u64 = cols[7].parse().unwrap_or(0);
        if let Some(entry) = state.get_mut(&l) {
            // Only count chunks that the runlog records as done; otherwise
            // a malformed/interrupted line could double-count.
            if ci != u64::MAX && entry.done_chunks.contains_key(&ci) {
                *entry.done_shifts.entry(a).or_insert(0) += cnt;
            }
        }
    }
}

fn epoch_secs() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs()
}

fn ensure_header(path: &Path) -> std::io::Result<()> {
    if path.exists() {
        return Ok(());
    }
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let mut f = File::create(path)?;
    writeln!(f, "# obstruction-residues runlog (TSV)")?;
    writeln!(
        f,
        "# kind\tL\tchunk_idx\tchunk_size\tk_start\tk_end\tcount\twall_sec\tts_epoch"
    )?;
    Ok(())
}

fn ensure_stats_header(path: &Path) -> std::io::Result<()> {
    if path.exists() {
        return Ok(());
    }
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let mut f = File::create(path)?;
    writeln!(f, "# obstruction-residues shift-class statistics (TSV)")?;
    writeln!(f, "# Per-chunk shift counts: chunk_shift\\tL\\tchunk_idx\\tchunk_size\\tk_start\\tk_end\\ta\\tcount")?;
    writeln!(f, "# Per-level totals:      level_shift\\tL\\t-\\t-\\t-\\t-\\ta\\tcount")?;
    writeln!(f, "# kind\tL\tchunk_idx\tchunk_size\tk_start\tk_end\ta\tcount")?;
    Ok(())
}

fn run_level(
    l: u32,
    chunk_bits: u32,
    prior: &LevelState,
    log: &mut impl Write,
    stats: Option<&mut dyn Write>,
) -> std::io::Result<u64> {
    if l < 1 || l > 63 {
        panic!("L must be in 1..=63");
    }
    if prior.level_done {
        eprintln!(
            "L={:>2}: already complete (total={}), skipping",
            l, prior.level_total
        );
        return Ok(prior.level_total);
    }

    let half = 1u64 << (l - 1);
    let effective_bits = chunk_bits.min(l - 1);
    if let Some(prev_bits) = prior.chunk_bits_seen {
        if prev_bits != effective_bits {
            panic!(
                "L={}: prior runs used chunk_bits={}, current request {}; refusing to mix",
                l, prev_bits, effective_bits
            );
        }
    }
    let chunk_size = 1u64 << effective_bits;
    let n_chunks = half / chunk_size; // half is a power of 2, chunk_size divides it

    let level_start = Instant::now();
    let mut total: u64 = prior.done_chunks.values().sum();
    let mut already = prior.done_chunks.len() as u64;
    if already > 0 {
        eprintln!(
            "L={:>2}: resuming with {}/{} chunks complete, partial total={}",
            l, already, n_chunks, total
        );
    }
    // Accumulator for the per-level shift distribution. Built up across
    // chunks; flushed as level_shift rows after the last chunk. If the run
    // is interrupted between chunks the partial sum is in chunk_shift rows.
    // On resume, seed with the per-shift sum already gathered from chunks
    // completed in prior runs (read from the stats output by read_stats);
    // otherwise the level_shift row would only reflect the post-resume
    // chunks. Empty if --stats-output wasn't used previously.
    let mut level_shifts: HashMap<i32, u64> = prior.done_shifts.clone();
    let mut stats = stats;

    for ci in 0..n_chunks {
        if prior.done_chunks.contains_key(&ci) {
            continue;
        }
        let k_start = ci * chunk_size;
        let k_end = k_start + chunk_size;
        let t0 = Instant::now();
        let chunk_shifts = count_chunk_shifts(l, k_start, k_end);
        let c: u64 = chunk_shifts.values().sum();
        let wall = t0.elapsed().as_secs_f64();
        let ts = epoch_secs();
        writeln!(
            log,
            "chunk\t{}\t{}\t{}\t{}\t{}\t{}\t{:.3}\t{}",
            l, ci, chunk_size, k_start, k_end, c, wall, ts
        )?;
        log.flush()?;
        if let Some(s) = stats.as_deref_mut() {
            // Stable ordering: sorted by a ascending.
            let mut keys: Vec<i32> = chunk_shifts.keys().copied().collect();
            keys.sort();
            for a in &keys {
                let cnt = chunk_shifts[a];
                writeln!(
                    s,
                    "chunk_shift\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
                    l, ci, chunk_size, k_start, k_end, a, cnt
                )?;
            }
            s.flush()?;
        }
        for (a, cnt) in &chunk_shifts {
            *level_shifts.entry(*a).or_insert(0) += cnt;
        }
        total += c;
        already += 1;
        eprintln!(
            "L={:>2}: chunk {:>4}/{}  cnt={:>12}  wall={:>7.2}s  total={:>15}  ({:.1}% done)",
            l,
            already,
            n_chunks,
            c,
            wall,
            total,
            100.0 * already as f64 / n_chunks as f64
        );
    }

    let level_wall = level_start.elapsed().as_secs_f64();
    let ts = epoch_secs();
    writeln!(
        log,
        "level\t{}\t-\t-\t-\t-\t{}\t{:.3}\t{}",
        l, total, level_wall, ts
    )?;
    log.flush()?;
    if let Some(s) = stats.as_deref_mut() {
        let mut keys: Vec<i32> = level_shifts.keys().copied().collect();
        keys.sort();
        for a in &keys {
            writeln!(
                s,
                "level_shift\t{}\t-\t-\t-\t-\t{}\t{}",
                l, a, level_shifts[a]
            )?;
        }
        s.flush()?;
    }
    eprintln!(
        "L={:>2}: DONE  total={}  ratio={:.8}  wall={:.1}s",
        l,
        total,
        total as f64 / (1u128 << l) as f64,
        level_wall
    );
    Ok(total)
}

// -------- CLI --------

struct Cli {
    l_start: u32,
    l_end: u32,
    output: PathBuf,
    stats_output: Option<PathBuf>,
    chunk_bits: u32,
    resume: bool,
}

fn print_usage(prog: &str) {
    eprintln!(
        "Usage: {} L_start [L_end] [--output FILE] [--stats-output FILE] [--chunk-bits N] [--resume]\n\n\
         Enumerate |Obs_L| for L in [L_start, L_end].\n\n\
         --output FILE         append-only TSV runlog (default: ./obs_runlog.tsv)\n\
         --stats-output FILE   if set, write per-chunk and per-level shift-class\n\
                               distribution to this TSV (separate from --output)\n\
         --chunk-bits N        process 2^N odd r per chunk (default: 24)\n\
         --resume              skip chunks/levels already recorded in --output",
        prog
    );
}

fn parse_cli() -> Cli {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        print_usage(&args[0]);
        std::process::exit(1);
    }
    let mut output = PathBuf::from("./obs_runlog.tsv");
    let mut stats_output: Option<PathBuf> = None;
    let mut chunk_bits: u32 = 24;
    let mut resume = false;
    let mut positionals: Vec<String> = Vec::new();
    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--output" => {
                i += 1;
                output = PathBuf::from(&args[i]);
            }
            "--stats-output" => {
                i += 1;
                stats_output = Some(PathBuf::from(&args[i]));
            }
            "--chunk-bits" => {
                i += 1;
                chunk_bits = args[i].parse().expect("--chunk-bits expects u32");
            }
            "--resume" => {
                resume = true;
            }
            "-h" | "--help" => {
                print_usage(&args[0]);
                std::process::exit(0);
            }
            other => positionals.push(other.to_string()),
        }
        i += 1;
    }
    if positionals.is_empty() {
        print_usage(&args[0]);
        std::process::exit(1);
    }
    let l_start: u32 = positionals[0].parse().expect("L_start must be int");
    let l_end: u32 = positionals
        .get(1)
        .map(|s| s.parse().expect("L_end must be int"))
        .unwrap_or(l_start);
    assert!(l_start <= l_end, "L_start must be <= L_end");
    Cli {
        l_start,
        l_end,
        output,
        stats_output,
        chunk_bits,
        resume,
    }
}

fn main() -> std::io::Result<()> {
    let cli = parse_cli();
    let n_threads = rayon::current_num_threads();
    eprintln!(
        "# rayon threads: {}  chunk_bits: {}  output: {}  stats: {}  resume: {}",
        n_threads,
        cli.chunk_bits,
        cli.output.display(),
        cli.stats_output
            .as_ref()
            .map(|p| p.display().to_string())
            .unwrap_or_else(|| "<none>".to_string()),
        cli.resume
    );

    let prior = if cli.resume {
        let mut s = read_runlog(&cli.output);
        if let Some(p) = &cli.stats_output {
            read_stats(p, &mut s);
        }
        s
    } else {
        if cli.output.exists() {
            eprintln!(
                "ERROR: --output {} exists. Pass --resume to continue, or remove it.",
                cli.output.display()
            );
            std::process::exit(2);
        }
        if let Some(p) = &cli.stats_output {
            if p.exists() {
                eprintln!(
                    "ERROR: --stats-output {} exists. Pass --resume to continue, or remove it.",
                    p.display()
                );
                std::process::exit(2);
            }
        }
        HashMap::new()
    };

    ensure_header(&cli.output)?;
    let mut log = OpenOptions::new().append(true).open(&cli.output)?;
    let mut stats_file = if let Some(p) = &cli.stats_output {
        ensure_stats_header(p)?;
        Some(OpenOptions::new().append(true).open(p)?)
    } else {
        None
    };

    println!(
        "# {:>3} {:>16} {:>14} {:>12}",
        "L", "|Obs_L|", "ratio", "wall_sec"
    );

    let mut prev: Option<u64> = None;
    for l in cli.l_start..=cli.l_end {
        let entry_default = LevelState::default();
        let entry = prior.get(&l).unwrap_or(&entry_default);
        let level_start = Instant::now();
        let n = run_level(
            l,
            cli.chunk_bits,
            entry,
            &mut log,
            stats_file.as_mut().map(|f| f as &mut dyn Write),
        )?;
        let wall = level_start.elapsed().as_secs_f64();
        let ratio = n as f64 / (1u128 << l) as f64;
        let lift = match prev {
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
            "  {:>3} {:>16} {:>14.8} {:>12.3}{}",
            l, n, ratio, wall, lift
        );
        prev = Some(n);
    }
    Ok(())
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
    fn chunked_equals_full() {
        // Splitting into chunks must give the same total as a single sweep.
        for l in 5u32..=14 {
            let full = count(l);
            let half = 1u64 << (l - 1);
            let chunk_bits = (l - 1).min(3); // small chunks to exercise the path
            let chunk_size = 1u64 << chunk_bits;
            let n_chunks = half / chunk_size;
            let chunked: u64 = (0..n_chunks)
                .map(|ci| count_chunk(l, ci * chunk_size, (ci + 1) * chunk_size))
                .sum();
            assert_eq!(full, chunked, "L={}: chunked {} != full {}", l, chunked, full);
        }
    }
}
