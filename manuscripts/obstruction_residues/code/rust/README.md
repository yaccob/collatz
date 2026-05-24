# High-performance enumeration of $\lvert\mathrm{Obs}_L\rvert$

Rust counterpart to `../python/count_obstructions.py`, designed to push the
rigorous lower bound

  $c_W \ge \lvert\mathrm{Obs}_L\rvert / 2^L$

(Theorem density-intro) to higher levels $L$ than is feasible in
Python. The algorithm is identical — parallel two-track $T_-$ reduction,
acceptance iff $X_{\mathrm{end}}(r, L) = 3 d_J + c_J = 1$ — but the
rational arithmetic uses a custom dyadic representation
(`i128` numerator, `i32` exponent), and the enumeration over odd
$r \in \{1, \dots, 2^L\}$ runs in parallel via `rayon`.

## Build

    cargo build --release

## Run

    ./target/release/count_obstructions_rs L_start [L_end] [flags]

Flags:

    --output FILE     append-only TSV runlog (default: ./obs_runlog.tsv)
    --chunk-bits N    process 2^N odd r per chunk (default: 24)
    --resume          skip chunks/levels already recorded in --output

Examples:

    # single level, default runlog in cwd
    ./target/release/count_obstructions_rs 24

    # sweep, writing to a stable location outside the repo
    ./target/release/count_obstructions_rs 5 28 \
      --output ~/research/obs_runlog.tsv

    # if the above is interrupted partway through L=28, resume:
    ./target/release/count_obstructions_rs 5 28 \
      --output ~/research/obs_runlog.tsv --resume

Each row in the stdout summary reports $\lvert\mathcal{O}_L\rvert$, the resulting
ratio $\lvert\mathcal{O}_L\rvert/2^L$, the wall-clock time, and (for $L >$
`L_start`) the lift-balance check $\lvert\mathcal{O}_L\rvert - 2\lvert\mathcal{O}_{L-1}\rvert$
(Corollary lift-balance).

## Checkpoint / resume

Within each level $L$, work is split into chunks of $2^N$ odd $r$
each (where $N$ is the value of `--chunk-bits`), processed sequentially
with internal rayon parallelism.
After each chunk completes, one line is appended to the runlog (TSV):

    chunk    L  chunk_idx  chunk_size  k_start  k_end  count  wall_sec  ts_epoch

When a level finishes, a `level` line is appended:

    level    L  -          -           -        -      total  wall_sec  ts_epoch

With `--resume`, the binary reads the runlog before starting: levels
with a `level` line are skipped entirely, partially-completed levels
resume from the first chunk not recorded. The chunk_bits used on resume
must match what is recorded; otherwise the binary refuses to mix.

Practical guidance:

- `--chunk-bits 24` (default) gives chunks of ~16M odd $r$. On 8 cores
  this is ~1–2 s per chunk at $L \approx 32$, scaling roughly $\times 2$
  per added $L$. Crash granularity is therefore at most one chunk lost
  ($\le 10$ s of work at $L = 36$, $\sim 1$ min at $L = 40$).
- `--chunk-bits` smaller than the level allows: clamps to $L - 1$
  automatically.
- The runlog is append-only and crash-safe (each chunk line is `flush()`-ed).

## Verification

    cargo test --release

cross-checks `count(L)` against the Table tab:appendix-counts values for
$L = 5, \dots, 16$ from the manuscript, and asserts the lift balance
$\lvert\mathcal{O}_L\rvert \ge 2\lvert\mathcal{O}_{L-1}\rvert$ at every level up to $L = 14$.

## Observed scaling (8 cores, M1-class)

| $L$ | $\lvert\mathcal{O}_L\rvert$ | $\rho_L$  | wall   |
|----:|----------------------------:|----------:|-------:|
| 16  |                       7 556 | 0.115295  |   1 ms |
| 20  |                     132 078 | 0.125959  |   9 ms |
| 24  |                   2 251 983 | 0.134229  | 160 ms |
| 28  |                  37 876 608 | 0.141101  |   3 s  |
| 32  |                 631 538 769 | 0.147042  |  55 s  |

Doubling $L$ multiplies wall time by ~30 — the per-$L$ factor is ~2.1,
matching the expected $2 \cdot \rho_L^{\text{work}}$ with the per-element
reduction taking $\Theta(L)$ steps.

## Limits

- `L <= 63` is enforced (uses `u64` for residue indexing).
- Trajectory values $a_K, a_I$ use `u128` and stay well below overflow
  for any $L$ in the reachable range.
- Numerators of the dyadic state are bounded by $3^L$ in absolute value,
  which fits in `i128` for $L \le 80$.
