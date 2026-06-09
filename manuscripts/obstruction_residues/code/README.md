# Supporting code for *Obstruction residues for the $3n-1$ map*

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
| `count_obstructions.py` | Appendix table (counts $\lvert\mathcal{O}_L\rvert$, $\lvert\mathcal{O}_L^{G_0}\rvert$, $\lvert\mathcal{O}_L^{G_{\ne 0}}\rvert$, $\lvert\mathcal{A}_L^{G_{\ne 0}}\rvert$) and the element lists of $\mathcal{O}_L$ and $\mathcal{A}_L^{G_{\ne 0}}$ (truncated at 30 entries), **and asserts** the strict lift balance $\lvert\mathcal{O}_L\rvert = 2\lvert\mathcal{O}_{L-1}\rvert + \lvert\mathcal{A}_L^{G_{\ne 0}}\rvert$ (`cor:lift-balance`) against the level-$(L-1)$ count. |
| `independent_enumeration.py` | The same appendix counts $\lvert\mathcal{O}_L\rvert$ for $5 \le L \le 16$, recomputed by a deliberately **independent algorithm** as a cross-check oracle. `count_obstructions.py` and the Rust port both propagate the affine pair $(c, d)$ through the recursion of the affine-relation lemma (`lem:affine`); this script instead iterates the two $T_-$ trajectories directly and reconstructs $X_{\mathrm{end}}$ from the terminal states in pure integer arithmetic (no `Fraction`, no dyadic struct). Asserts every count against the table published in the manuscript; with `--cross-check` it additionally asserts, element by element, that its $\mathcal{O}_L$ coincides with the set produced by `count_obstructions.py`. Guards against a systematic error shared by the canonical implementation and its line-by-line mirror. |
| `atomic_anchor_verification.py` | Atom decomposition (`lem:atom-decomp`): every obstruction has a unique atomic anchor. |
| `atomic_g0_early_stop_check.py` | No shift-zero atoms (`thm:no-G0-atom`): no atomic shift-zero obstructions at level $\ge 7$. Classifies the lift origin of every $G_0$-obstruction. |
| `factor_complexity_construction.py` | Full factor complexity, constructive form (`thm:fc-intro`): for every $u \in \{0,1\}^n$ and every base anchor $r_0 \in \mathcal{O}_6$, the constructive lift produces a residue in $\mathcal{O}_{6+n}$ whose binary representation contains $u$ as a factor. Checked for $n \le 10$. |
| `lift_lemma_test.py` | Lift theorem (`thm:lift-plus` / `thm:lift-minus`): empirical confirmation that both $r_+$ and $r_-$ are obstructions for every obstruction at $5 \le L_0 \le 12$. |
| `lift_symmetry_verification.py` | Lift symmetry (`prop:lift-symmetry`): stop-type vs. resulting shift-index. |
| `iso_synchronisation_verification.py` | Simultaneous stop (`cor:sync`) and parity at termination (`lem:parity`): K- and I-track terminate at the same index, and the cumulative valuations satisfy $V_K^{(J)} - V_I^{(J)} = v$ at the terminal index. Verified for all $G_0$-obstructions at $L \le 16$. |
| `x_invariant_bidirectional.py` | Obstruction-residue definition (`def:obstruction`): bidirectional consistency of the algebraic $X$-criterion with the dynamical stopping-time criterion across all odd residues $r$ with $v_2(r-1) \ge 1$, $5 \le L \le 12$. |
| `x_invariant_non_obstructions.py` | Same as above, restricted to classes with $v_2(r-1) = 1$ (i.e. $r \equiv 3 \pmod 4$). |
| `tplus_bijection_verification.py` | Residue involution / bijection (`lem:involution-step` / `thm:tplus-bijection`): the involution $r \mapsto (-r) \bmod 2^L$ maps the T_- parallel reduction to the T_+ parallel reduction step-by-step, with terminal data related by $(c^+_J, d^+_J) = (c^-_J, -d^-_J)$; with the sign convention $X^+ := c - 3d$ (`rem:Xplus-sign`) the X-criteria coincide and $\mathcal{O}_L \leftrightarrow \mathcal{O}_L^+$. |

The next group certifies the shift-index window (`sec:shift-window`): the depth
bound $J \ge 2\lvert s\rvert + 3$ (`thm:depth`) and its corollary
$s \le \lfloor (L-5)/4\rfloor$ (`cor:shift-window`).

| Script | Verifies |
|:---|:---|
| `signfree_identity_check.py` | Sign-free obstruction identity (`lem:signfree`): the identity holds for every obstruction at $5 \le L \le 19$, for both shift signs (126648 obstructions, of which 1881 have $s < 0$); the equivalent $O''$-form is checked alongside. |
| `depth_bound_threshold.py` | Large negative shift (`lem:depth-negbig`): the necessary condition $3^{J+1} > 2^{J+2\lvert s\rvert}$ forces $J \ge 2\lvert s\rvert + 3$ for $\lvert s\rvert \ge 4$, with the exact threshold $\tfrac{27}{4}(9/16)^{\lvert s\rvert} < 1 \iff \lvert s\rvert \ge 4$. |
| `depth_closed_form.py` | Large positive shift (`lem:depth-posbig`): the extremal sums $A_K^{\min}, A_I^{\max}$ against a brute optimisation over the structural families, the factorisation $D = C_0 + 2^{v+q}\Gamma$, and the positivity ($\Gamma > 0$, $\Phi > 3$, $D(J,s,v,0) > 0$) over $1 \le v \le J \le 2s+2$ for $s \ge 4$; reports the finite residual cells for $s \in \{2,3\}$. |
| `depth_carry_automaton_k2.py` | Bounded carry automaton (`lem:carry-automaton`), positive stratum $(s{=}2, J{=}6)$: the block-A fixed point ($P=1$) rejects all $q$; the carry-DP is validated against the coupled $(v_K,v_I)$-DFS on zero and nonzero targets. |
| `depth_carry_automaton_neg.py` | Bounded carry automaton (`lem:carry-automaton`), negative strata $(2,5),(2,6),(3,8)$: each fixed point rejects all $q$; the exact DP is validated against the trajectory oracle (0 mismatches, incl. the tight obstruction $r = 1015979$). |
| `depth_carry_statespace.py` | Finite-state-space certificate for the $(s{=}2, J{=}6)$ automaton: at most 185 reachable states, the invariant carry interval $[-81, 81]$ entered within two block-A steps. |
| `depth_dfs_tails.py` | Small-shift tails (`lem:finite-tails`), positive residuals: $s{=}3$ ($J{=}8, q{=}0, v \in [2,8]$; 4096 sequences) and $s{=}2$ ($J{=}5, q \in \{0,1\}$; 1443 sequences), each with 0 obstructions, by exhaustive coupled DFS. |
| `shift_index_window_check.py` | Depth bound (`thm:depth`) and window (`cor:shift-window`): both verified directly over all obstructions at $5 \le L \le 20$. |

A meta-test (`meta_test_exit_convention.py`) statically verifies that every
script in the tables above exits with non-zero status when its check detects
a violation.

### Auxiliary / heuristic

Supporting checks that produce data but do not assert a rigorous theorem. Read
the script header for what claim (if any) is being explored.

| Script | Status |
|:---|:---|
| `obstr_factor_complexity.py` | Empirical enumeration of $p_W(n)$ at finite $L$: produces scaling data consistent with $p_W(n) = 2^n$ (`thm:fc-intro`) but does not certify the asymptotic identity. For $n$ close to or exceeding $L$ the displayed value is below $2^n$ — a finite-$L$ artefact, not a refutation. The complementary `factor_complexity_construction.py` delivers the constructive direction with a hard pass/fail. |
| `obstr_factor_uniformity.py` | Pattern-distribution statistics for the quasi-uniformity heuristic. No rigorous claim attached. |
| `lift_case_analysis.py` | Case-distribution table for stop types EE and SS at fixed $L_0$. Auxiliary support for §3. |
| `shift_index_regime.py` | Empirical tightness of the depth bound $J \ge 2\lvert s\rvert + 3$ (`thm:depth`): per signed $s$, the minimum $J$ and the tightest instance (e.g. $r = 15877$ for $s = 2$, $r = 1015979$ for $s = -2$, both at $J = 7$). Produces data only; asserts nothing. |

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
