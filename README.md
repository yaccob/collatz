# collatz

Publication-ready manuscripts and supporting code on the $3x+1$ problem.

## Layout

```
.
├── Makefile                       build orchestration
├── README.md                      this file
├── .githooks/                     versioned git hooks (pre-commit PDF rebuild)
└── manuscripts/                      one directory per manuscript (<slug>/),
                                      each with <slug>.tex, <slug>.pdf (kept in
                                      sync via pre-commit hook), references.bib,
                                      and code/ (verification scripts)
    ├── obstruction_residues/         obstruction-residue theory for the 3x-1 map
    ├── obstruction_residues_family/  the (an+b) family: uniform theory across multipliers
    └── negative_mersenne/            negative-Mersenne multipliers a = -(2^k - 1)
```

## Build

```sh
make papers          # build all manuscript PDFs in this repo
make clean           # remove all build artefacts (_build/, __pycache__/)
make check           # sanity check (currently: all tracked .py parse)
make install-hooks   # enable .githooks/pre-commit (one-time per clone)
```

Convention: a manuscript is a directory `manuscripts/<slug>/` containing
`<slug>.tex`. The built PDF is placed next to its source.

Requires TeX Live (`latexmk`, `pdflatex`, `bibtex`) and Python 3.10+.

After cloning, run `make install-hooks` once. The pre-commit hook then
rebuilds and re-stages any manuscript PDF whenever its TeX source or
bibliography is part of a commit, so committed PDFs stay in sync with
their sources.

## Manuscripts

### obstruction_residues

*Obstruction residues for the $3x-1$ map: full factor complexity,
positive density, and a constructive lift.* Manuscript proves a
constructive lift theorem, a series representation of the asymptotic
obstruction density, full factor complexity $p_W(n) = 2^n$ of the
associated binary language, and structural-rigidity corollaries
(the family is not a subshift of finite type, not a sofic shift, not
a primitive substitution shift). See `manuscripts/obstruction_residues/obstruction_residues.tex`
for the full text and `manuscripts/obstruction_residues/code/README.md` for the
mapping between scripts and verified results.

### obstruction_residues_family

*Obstruction residues for the $(an+b)$ family: a uniform theory across
multipliers.* Develops a bias-axis conjugation making cardinality and density
depend only on the multiplier $a$, a multiplier-order lemma, the existence of
the asymptotic density, and a no-shift-zero-atom theorem; it flags the
negative-Mersenne case as admitting a finer structure, treated in the next
manuscript. See `manuscripts/obstruction_residues_family/` for the text and its
`code/README.md` for the script-to-result mapping.

### negative_mersenne

*Obstruction residues at negative-Mersenne multipliers: a synchronisation
hierarchy and density bounds.* Isolates the multipliers $a = -q$,
$q = 2^{v_M}-1$, and develops the finer structure the family theory flags as
case-specific: an exact Mersenne-only identity, a recursion on an affine
certificate, level-3 and level-4 sub-class classifications, a node-lift
theorem, a density lower bound $c_W^{(-q)} \ge 1/(2q)$ (asymptotically sharp as
$v_M \to \infty$ under a stated completeness hypothesis), and an observability
bound. See `manuscripts/negative_mersenne/` for the text and its
`code/README.md` for the script-to-result mapping.

## License

- Manuscripts and other text/figure content: [CC-BY 4.0](LICENSE).
- Verification code under `manuscripts/*/code/`: [MIT](manuscripts/obstruction_residues/code/LICENSE).
