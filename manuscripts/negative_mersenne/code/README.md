# Supporting code for *Obstruction residues at negative-Mersenne multipliers*

Reference enumerators and falsifiers for the manuscript
(`../negative_mersenne.tex`). Each script re-derives a theorem-bound claim or a
concrete table/prose number from unhacked enumeration and asserts it (printing
`CONFIRM` / `FALSIFY`, exit `0` / `1`), so a broken claim surfaces as a hard
failure rather than silently.

## Layout

- **`python/`** — single-file, `fractions`-based enumerators, deliberately
  simple so the algebra reads against the text. They are cited by
  `\srcpath{code/python/...}` in the manuscript:

  | Script | Verifies (manuscript section) |
  |---|---|
  | `identity.py` | main identity + Mersenne-sync + non-Mersenne (§3) |
  | `recursion.py` | recursion theorem, level-4 sync identities, node lift (§4, 6, 7) |
  | `stage3.py` | level-3 structure: family count, `K_A`/`K_B`, concrete counts (§5) |
  | `stage4_enum.py` | exhaustive level-4 sub-class count (§6) |
  | `atom_density.py` | density lower bound, refined bound, Table 1 (§8) |
  | `refined_decomposition.py` | per-family decomposition of the refined bound (§8) |
  | `j_bound.py` | observability bound (§9) |

  `_reduction.py` is the shared two-track reduction helper imported by the
  others; it is not a standalone check.

## Running

Each check is standalone and needs no third-party dependencies:

    python3 python/<name>.py

It prints `CONFIRM` and exits `0` when the claim holds, or `FALSIFY` and exits
`1` on a counterexample.

## Naming convention (bias `b` vs `c`)

The manuscript writes the bias as `b` (the map `T_{-q,b}`). The code calls it
`c` (`T_{-q,c}`): the `b`-root is reserved for the modulus tracks `b_K, b_I`
carried alongside `a_K, a_I` in the parallel reduction, so reusing `b` for the
bias would collide. This is the same `c`-for-bias convention used in the
companion `(an+b)`-family manuscript's code.

## License

MIT (see `LICENSE`), as for all verification code under `manuscripts/*/code/`;
the manuscript text itself is CC-BY 4.0 (repository-root `LICENSE`).

## Archival / DOI

This paper has no separate Zenodo DOI; it is archived as part of the main
repository (`github.com/yaccob/collatz`) under that repository's Zenodo
software record (concept DOI `10.5281/zenodo.20356496`) via the Zenodo–GitHub
release integration.
