# collatz

Publication-ready manuscripts and supporting code on the $3x \pm 1$
problem and adjacent residue-dynamical questions.

## Layout

```
manuscripts/
└── t_minus/            obstruction-residue theory for the 3x-1 map
    ├── obstructions.tex   LaTeX source (amsart)
    ├── obstructions.md    Markdown draft predecessor
    ├── references.bib     BibTeX bibliography
    └── code/              verification scripts (pure Python stdlib)
```

## Build

```sh
make paper           # build manuscripts/t_minus/_build/obstructions.pdf
make paper-clean     # remove build artefacts
make check-py        # py_compile sanity check on all tracked Python
```

Requires TeX Live (`latexmk`, `pdflatex`, `bibtex`) and Python 3.10+.

## Manuscripts

### t_minus

*Obstruction residues for the $3x-1$ map: full factor complexity,
positive density, and a constructive lift.* Manuscript proves a
constructive lift theorem, a series representation of the asymptotic
obstruction density, full factor complexity $p_W(n) = 2^n$ of the
associated binary language, and structural-rigidity corollaries
(the family is not a subshift of finite type, not a sofic shift, not
a primitive substitution shift). See `manuscripts/t_minus/obstructions.tex`
for the full text and `manuscripts/t_minus/code/README.md` for the
mapping between scripts and verified results.
