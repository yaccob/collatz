# Supporting code for *Obstruction residues for the $(an+b)$ family*

This directory holds the verification code for the manuscript. It has two
layers:

- **`python/`** — reference enumerators, cited by `\srcpath{...}` in the
  manuscript. They are deliberately simple (`fractions`-based, single-file)
  so the algebra is easy to read against the text.
- **`rust/`** — the performant, reach-extending falsifiers (a Cargo
  workspace). They re-derive, from unhacked enumeration, every theorem-bound
  claim and every concrete table/prose number in the manuscript. The Python
  scripts here are the human-readable counterpart; the Rust suite is the
  authoritative check.

## Archival / DOI

This paper does **not** get its own Zenodo DOI. Once this manuscript and its
code are released as part of the main repository
(`github.com/yaccob/collatz`), they are archived under that repository's
existing Zenodo software record (concept DOI `10.5281/zenodo.20356496`,
resolving to the latest version) via the Zenodo↔GitHub release integration.
At submission, cite the **concept DOI** for the living archive and the
**version DOI** of the specific release that contains this paper's code (the
exact, reproducible state). The Zenodo record is repo-level (it archives all
manuscripts plus their verification code), not specific to any single paper.

## Reference enumerators (`python/`)

Each is a standalone `python3 <name>.py` run (no third-party dependencies);
`factor_lang_check.py` and `conjugation_check.py` import `alternative_setups`,
`negative_a_first_obstructions.py` imports `count_obstructions_ac`, all from
this directory.

**Naming convention.** The code calls the bias parameter `c`, where the
manuscript writes `b` (so $T_{a,c}$ here is the manuscript's $T_{a,b}$). The
`b`-root is deliberately reserved for the modulus tracks `b_K, b_I` (the
manuscript's $b_K^{(j)}, b_I^{(j)}$), which the reduction carries alongside
`a_K, a_I`; reusing `b` for the bias would collide with them. The same
`c`-for-bias convention is used in the Rust gate (`lib.rs`: $T_{a,c}$).

| Script | Verifies / supports |
|:---|:---|
| `count_obstructions_ac.py` | Generic $(a,b)$ obstruction enumeration; $J$-distribution; $L_{\min}$, $J_{\max}$ and density tables (Sections on $L_{\min}$, structure, and scaling). |
| `factor_lang_check.py` | $b$-axis universality: $\lvert\mathcal{O}_{12}^{(3,b)}\rvert = 409$ for all odd $b$, zero shift-index mismatches (Theorem, Conjugation). |
| `conjugation_check.py` | Conjugation theorem: shift-preserving bijection $\Psi_b$. |
| `negative_a_first_obstructions.py` | Degenerate case $a = -1$: confirms $\lvert\mathcal{O}_L^{(-1,b)}\rvert = 2^{L-2}$ (Remark on $a=-1$). |
| `alternative_setups.py` | Variant-B reduction $m := (r + b)/2^v$; imported by `factor_lang_check.py` and `conjugation_check.py`. |

## Machine-checked verification (build gate)

The Rust falsifiers under `rust/src/bin/` formalise
the manuscript's claims as hard pass/fail (`CONFIRM`/`FALSIFY`) checks,
including the items that were sketch-only in earlier drafts:

- `j1_characterization.rs` — the $J=1$ power-of-two criterion
  $a-1+2^v = 2^w k_a$ (realisability by construction up to large $a$, plus a
  necessity sweep);
- `no_G0_atom.rs` — the generalised no-shift-zero-atom theorem (every
  shift-zero obstruction is a lift);
- `atom_bound_fixed_J.rs` — the fixed-$J$ polynomial atom bound
  $\le \binom{L-1}{J}$;
- `empirical_tables.rs` — every concrete enumerated number (order table,
  scaling cardinalities + $C(a)$ + the log-linear fit, $J$-statistics counts/
  means/$J_{\max}$, $J_{\max}$-over-$a$, $\lvert\mathcal{O}_{12}^{(3,b)}\rvert=409$,
  sparse counts, $\lvert a\rvert=11$ vacuity, the A3 witnesses);
- plus `conjugation.rs`, `order_lemma.rs`, `diophantine_identity.rs`,
  `lift.rs`, `lmin_lower.rs`, `lminus4_atom.rs`, `degenerate_a1.rs`.

Every claim-labelled theorem/lemma/proposition/corollary is either backed by
a check above or is a conjecture, intro preview, or auxiliary lemma.
