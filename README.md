# collatz

Publication-ready manuscripts and supporting code on the $3x \pm 1$
problem and adjacent residue-dynamical questions.

## Layout

```
.
├── Makefile                       build orchestration
├── README.md                      this file
└── manuscripts/
    └── obstruction_residues/      obstruction-residue theory for the 3x-1 map
        ├── obstruction_residues.tex   LaTeX source (amsart)
        ├── references.bib             BibTeX bibliography
        └── code/                      verification scripts (pure Python stdlib)
```

## Build

```sh
make paper           # build manuscripts/obstruction_residues/_build/obstruction_residues.pdf
make paper-clean     # remove build artefacts
make check-py        # py_compile sanity check on all tracked Python
```

Requires TeX Live (`latexmk`, `pdflatex`, `bibtex`) and Python 3.10+.

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
