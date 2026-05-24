# Supporting code for *Obstruction residues for the $3x-1$ map*

This directory contains the verification code referenced in the
appendix of the manuscript `obstruction_residues.tex`. Each script enumerates
a finite range of obstruction residues, runs the parallel reduction
defined in §2 of the paper, and reports the result.

## Layout

- `python/` — Python verification scripts (one per rigorous result; pure
  stdlib, no third-party dependencies). The bulk of the appendix table is
  verified here.
- `rust/` — Rust enumerator (`obstruction_residues_count`) that pushes the
  level $L$ further than is feasible in Python; runs the same algorithm.
- `LICENSE` — MIT, applies to both `python/` and `rust/`.

## Requirements

- Python 3.10 or newer for `python/` (uses `fractions.Fraction` and standard
  library only; no third-party dependencies).
- Rust toolchain (`cargo`, stable channel) for `rust/`.

## Scripts and the results they verify

### Rigorous verification

Each script below produces a hard pass/fail for the named theorem and exits
non-zero on violation. Defaults are tuned for sub-second to few-second smoke
runs on a modern laptop; raising the level argument to $L = 16$ takes
30 seconds to a few minutes.

| Script | Verifies |
|:---|:---|
| `count_obstructions.py` | Appendix table (counts $\lvert\mathcal{O}_L\rvert$, $\lvert\mathcal{O}_L^{G_0}\rvert$, $\lvert\mathcal{O}_L^{G_{\ne 0}}\rvert$, $\lvert\mathcal{A}_L^{G_{\ne 0}}\rvert$) and the element lists of $\mathcal{O}_L$ and $\mathcal{A}_L^{G_{\ne 0}}$ (truncated at 30 entries), **and asserts** the strict lift balance $\lvert\mathcal{O}_L\rvert = 2\lvert\mathcal{O}_{L-1}\rvert + \lvert\mathcal{A}_L^{G_{\ne 0}}\rvert$ (Corollary 6.4) against the level-$(L-1)$ count. |
| `atomic_anchor_verification.py` | Lemma 6.1 (atom decomposition): every obstruction has a unique atomic anchor. |
| `atomic_g0_early_stop_check.py` | Theorem 6.2 (no shift-zero atoms): no atomic shift-zero obstructions at level $\ge 7$. Classifies the lift origin of every $G_0$-obstruction. |
| `factor_complexity_construction.py` | Theorem 1.3 (constructive form): for every $u \in \{0,1\}^n$ and every base anchor $r_0 \in \mathcal{O}_6$, the constructive lift produces a residue in $\mathcal{O}_{6+n}$ whose binary representation contains $u$ as a factor. Checked for $n \le 10$. |
| `lift_lemma_test.py` | Theorems 3.1 and 3.2 (lift theorem): empirical confirmation that both $r_+$ and $r_-$ are obstructions for every obstruction at $5 \le L_0 \le 12$. |
| `lift_symmetry_verification.py` | Proposition 3.3 (lift symmetry): stop-type vs. resulting shift-index. |
| `iso_synchronisation_verification.py` | Corollary 2.5 (simultaneous stop) and Lemma 2.4 (parity at termination): K- and I-track terminate at the same index, and the cumulative valuations satisfy $V_K^{(J)} - V_I^{(J)} = v$ at the terminal index. Verified for all $G_0$-obstructions at $L \le 16$. |
| `x_invariant_bidirectional.py` | Definition 2.2 (Subsection 2.4): bidirectional consistency of the algebraic $X$-criterion with the dynamical stopping-time criterion across all odd residues $r$ with $v_2(r-1) \ge 1$, $5 \le L \le 12$. |
| `x_invariant_non_obstructions.py` | Same as above, restricted to classes with $v_2(r-1) = 1$ (i.e. $r \equiv 3 \pmod 4$). |
| `tplus_bijection_verification.py` | Lemma 7.2 / Theorem 7.3 (T_-/T_+ bijection): the involution $r \mapsto (-r) \bmod 2^L$ maps the T_- parallel reduction to the T_+ parallel reduction step-by-step, with terminal data related by $(c^+_J, d^+_J) = (c^-_J, -d^-_J)$; with the sign convention $X^+ := c - 3d$ (Remark 7.1) the X-criteria coincide and $\mathcal{O}_L \leftrightarrow \mathcal{O}_L^+$. |

A meta-test (`meta_test_exit_convention.py`) statically verifies that every
script in the table above exits with non-zero status when its check detects
a violation.

### Auxiliary / heuristic

Supporting checks that produce data but do not assert a rigorous theorem. Read
the script header for what claim (if any) is being explored.

| Script | Status |
|:---|:---|
| `obstr_factor_complexity.py` | Empirical enumeration of $p_W(n)$ at finite $L$: produces scaling data consistent with $p_W(n) = 2^n$ (Theorem 1.3) but does not certify the asymptotic identity. For $n$ close to or exceeding $L$ the displayed value is below $2^n$ — a finite-$L$ artefact, not a refutation. The complementary `factor_complexity_construction.py` delivers the constructive direction with a hard pass/fail. |
| `obstr_factor_uniformity.py` | Pattern-distribution statistics for the quasi-uniformity heuristic. No rigorous claim attached. |
| `lift_case_analysis.py` | Case-distribution table for stop types EE and SS at fixed $L_0$. Auxiliary support for §3. |

## Usage

Each Python script is self-contained and can be run with no arguments
(default parameters chosen for a reasonable runtime), or with an optional
positional level argument:

```sh
python3 python/atomic_g0_early_stop_check.py            # default L
python3 python/atomic_g0_early_stop_check.py 14         # explicit level
```

The Rust enumerator is built and run from its own subdirectory:

```sh
cd rust/ && cargo build --release
./target/release/count_obstructions_rs 20            # single level
./target/release/count_obstructions_rs 5 28          # sweep L = 5..28
```

See `rust/README.md` for the full set of flags (chunked checkpoints,
`--resume`, custom runlog path).

Runtimes scale roughly as $O(L \cdot 2^L)$. Typical numbers for the
**Python** scripts on a modern laptop:

- $L = 12$: a few seconds per script.
- $L = 16$: 30 seconds to a few minutes.
- $L = 18$: 5–10 minutes for the heavier scripts.

The **Rust** enumerator in `rust/` runs the same algorithm but with a
custom dyadic representation and `rayon` parallelism, and pushes the
reachable level by roughly a factor of two. Indicative wall times on
an 8-core M1-class laptop:

- $L = 24$: ~0.2 s
- $L = 28$: ~3 s
- $L = 32$: ~55 s

See `rust/README.md` for the full scaling table, checkpoint/resume
flags, and verification harness.

## Reproducibility

This directory is hosted at
<https://github.com/yaccob/collatz/tree/main/manuscripts/obstruction_residues/code>
and permanently archived on Zenodo:

- Concept DOI (always resolves to the latest archived version):
  <https://doi.org/10.5281/zenodo.20356496>
- Version DOI for the `v0.1.0` snapshot:
  <https://doi.org/10.5281/zenodo.20356497>

For stable citation prefer the concept DOI; use the version DOI when
the exact archived snapshot matters (e.g. reviewer correspondence).
