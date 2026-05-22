# collatz

Publication-ready manuscripts and supporting code on the $3x+1$ problem.

## Layout

```
.
├── Makefile                       build orchestration
├── README.md                      this file
├── .githooks/                     versioned git hooks (pre-commit PDF rebuild)
└── manuscripts/
    └── obstruction_residues/      obstruction-residue theory for the 3x-1 map
        ├── obstruction_residues.tex   LaTeX source (amsart)
        ├── obstruction_residues.pdf   built PDF (kept in sync via pre-commit hook)
        ├── references.bib             BibTeX bibliography
        └── code/                      verification scripts (pure Python stdlib)
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
