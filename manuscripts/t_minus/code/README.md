# Supporting code for *Obstruction residues for the $3x-1$ map*

This directory contains the verification scripts referenced in the
appendix of the manuscript `obstructions.tex`. Each script enumerates
a finite range of obstruction residues, runs the parallel reduction
defined in §2 of the paper, and reports the result.

## Requirements

- Python 3.10 or newer (uses `fractions.Fraction` and standard library only;
  no third-party dependencies).

## Scripts and the results they verify

| Script | Verifies |
|:---|:---|
| `atomic_anchor_verification.py` | Lemma 6.1 (atom decomposition): every obstruction has a unique atomic anchor. |
| `atomic_g0_early_stop_check.py` | Theorem 6.2 (no shift-zero atoms): no atomic shift-zero obstructions at level $\ge 7$. Classifies the lift origin of every $G_0$-obstruction. |
| `obstr_factor_complexity.py` | Theorem 5.1 (full factor complexity): empirical confirmation $p_W(n) = 2^n$ for $n \le 12$ at $L \le 16$. |
| `obstr_factor_uniformity.py` | Section 5 auxiliary: pattern-distribution statistics for the quasi-uniformity heuristic. |
| `factor_complexity_construction.py` | Theorem 5.1 (constructive form): for every $u \in \{0,1\}^n$ and every base anchor $r_0 \in \mathcal{O}_6$, the constructive lift produces a residue in $\mathcal{O}_{6+n}$ whose binary representation contains $u$ as a factor. Checked for $n \le 10$. |
| `lift_lemma_test.py` | Theorems 3.1 and 3.2 (lift theorem): empirical confirmation that both $r_+$ and $r_-$ are obstructions for every obstruction at $L_0 \le 12$. |
| `lift_symmetry_verification.py` | Symmetry table in §3.3: stop-type vs. resulting shift-index. |
| `lift_case_analysis.py` | Auxiliary classification of stop types EE and SS. |
| `iso_synchronisation_verification.py` | Corollary 2.4 (simultaneous stop): K- and I-track terminate at the same index. Verified for all $G_0$-obstructions at $L \le 16$. |
| `x_invariant_bidirectional.py` | Definition 2.2 and Section 2.4 connection: bidirectional consistency of the algebraic $X$-criterion with the dynamical stopping-time criterion across all odd residues $r$ with $v_2(r-1) \ge 1$, $L \le 12$. |
| `x_invariant_non_obstructions.py` | Same as above, restricted to the non-obstruction complement. |

## Usage

Each script is self-contained and can be run with no arguments (default
parameters chosen for a reasonable runtime), or with an optional
positional level argument:

```sh
python atomic_g0_early_stop_check.py            # default L
python atomic_g0_early_stop_check.py 14         # explicit level
```

Runtimes scale roughly as $O(L \cdot 2^L)$. Typical numbers on a modern
laptop:

- $L = 12$: a few seconds per script.
- $L = 16$: 30 seconds to a few minutes.
- $L = 18$: 5–10 minutes for the heavier scripts.

## Reproducibility

This directory is hosted at
<https://github.com/yaccob/collatz/tree/main/manuscripts/t_minus/code>.
For stable citation, use that URL together with a specific commit hash
or release tag.
