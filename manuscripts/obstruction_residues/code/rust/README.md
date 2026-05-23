# High-performance enumeration of |Obs_L|

Rust counterpart to `../count_obstructions.py`, designed to push the
rigorous lower bound

  c_W >= |Obs_L| / 2^L

(Theorem density-intro) to higher levels $L$ than is feasible in
Python. The algorithm is identical — parallel two-track $T_-$ reduction,
acceptance iff $X_{\mathrm{end}}(r, L) = 3 d_J + c_J = 1$ — but the
rational arithmetic uses a custom dyadic representation
(`i128` numerator, `i32` exponent), and the enumeration over odd
$r \in \{1, \dots, 2^L\}$ runs in parallel via `rayon`.

## Build

    cargo build --release

## Run

    ./target/release/count_obstructions_rs L_start [L_end]

Examples:

    # single level
    ./target/release/count_obstructions_rs 24

    # sweep
    ./target/release/count_obstructions_rs 5 28

Each row reports $|\mathcal{O}_L|$, the resulting ratio
$|\mathcal{O}_L|/2^L$, the wall-clock time, and (for $L >$ `L_start`)
the lift-balance check $|\mathcal{O}_L| - 2|\mathcal{O}_{L-1}|$
(Corollary lift-balance).

## Verification

    cargo test --release

cross-checks `count(L)` against the Table tab:appendix-counts values for
$L = 5, \dots, 16$ from the manuscript, and asserts the lift balance
$|\mathcal{O}_L| \ge 2|\mathcal{O}_{L-1}|$ at every level up to $L = 14$.

## Observed scaling (8 cores, M1-class)

| $L$ | $|\mathcal{O}_L|$ | $\rho_L$  | wall   |
|----:|------------------:|----------:|-------:|
| 16  |             7 556 | 0.115295  |   1 ms |
| 20  |           132 078 | 0.125959  |   9 ms |
| 24  |         2 251 983 | 0.134229  | 160 ms |
| 28  |        37 876 608 | 0.141101  |   3 s  |
| 32  |       631 538 769 | 0.147042  |  55 s  |

Doubling $L$ multiplies wall time by ~30 — the per-$L$ factor is ~2.1,
matching the expected $2 \cdot \rho_L^{\text{work}}$ with the per-element
reduction taking $\Theta(L)$ steps.

## Limits

- `L <= 63` is enforced (uses `u64` for residue indexing).
- Trajectory values $a_K, a_I$ use `u128` and stay well below overflow
  for any $L$ in the reachable range.
- Numerators of the dyadic state are bounded by $3^L$ in absolute value,
  which fits in `i128` for $L \le 80$.
