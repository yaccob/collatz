#!/usr/bin/env python3
"""Enforce the repository's dual-licensing invariant.

The top-level README declares two license regimes: manuscript text and figures
are CC-BY 4.0 (top-level LICENSE), while the verification code under
`manuscripts/*/code/` is MIT-licensed. Each such code directory must therefore
carry its own MIT LICENSE file. This check fails if any `manuscripts/*/code/`
directory is missing a LICENSE, or its LICENSE is not MIT -- catching
regressions such as a manuscript's code being added to the tree without its
accompanying license.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
code_dirs = sorted(ROOT.glob("manuscripts/*/code"))

problems = []
if not code_dirs:
    problems.append("no manuscripts/*/code directories found -- glob misconfigured?")

for d in code_dirs:
    lic = d / "LICENSE"
    rel = lic.relative_to(ROOT)
    if not lic.is_file():
        problems.append(f"missing LICENSE: {rel}")
    elif "MIT License" not in lic.read_text(encoding="utf-8"):
        problems.append(f"LICENSE is not MIT: {rel}")

if problems:
    print("License invariant violated:", file=sys.stderr)
    for p in problems:
        print(f"  - {p}", file=sys.stderr)
    sys.exit(1)

print(f"License invariant OK: {len(code_dirs)} code dir(s) each carry an MIT LICENSE.")
