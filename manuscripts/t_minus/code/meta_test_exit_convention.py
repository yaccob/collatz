"""Meta-test: every script in the README's "Rigorous verification" table must
have a mechanism that exits with non-zero status when its check detects a
violation.

The README (this directory, section "Rigorous verification") promises:

    Each script below produces a hard pass/fail for the named theorem and
    exits non-zero on violation.

A CI runner, a Zenodo reproducibility check, or any human invoking the
scripts in a loop relies on this. A script that prints "FAILED" but exits
zero silently regresses.

This test enforces, statically, that each listed script contains at least
one of:

  - `sys.exit(<nonzero literal>)`, or
  - `sys.exit(<non-constant expression>)` (e.g. `sys.exit(1 if violations else 0)`), or
  - an `assert` statement, or
  - a `raise` statement.

This is a necessary condition, not a sufficient one: the test does not
verify the exit path is actually reachable from a real violation. But it
catches the present concrete bug (six scripts have no such mechanism at
all) and any future regression of the same shape.

Run with:  python3 meta_test_exit_convention.py
"""

import ast
import pathlib
import sys

CODE_DIR = pathlib.Path(__file__).resolve().parent

# Scripts the README's "Rigorous verification" table promises will exit
# non-zero on violation. obstr_factor_complexity.py is intentionally NOT in
# this list - it is heuristic-only (see review M-02).
RIGOROUS_SCRIPTS = [
    "atomic_anchor_verification.py",
    "atomic_g0_early_stop_check.py",
    "count_obstructions.py",
    "factor_complexity_construction.py",
    "iso_synchronisation_verification.py",
    "lift_lemma_test.py",
    "lift_symmetry_verification.py",
    "tplus_bijection_verification.py",
    "x_invariant_bidirectional.py",
    "x_invariant_non_obstructions.py",
]


def has_nonzero_exit_mechanism(source: str) -> bool:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assert, ast.Raise)):
            return True
        if isinstance(node, ast.Call):
            func = node.func
            is_sys_exit = (
                isinstance(func, ast.Attribute)
                and func.attr == "exit"
                and isinstance(func.value, ast.Name)
                and func.value.id == "sys"
            )
            if not is_sys_exit or not node.args:
                continue
            arg = node.args[0]
            if isinstance(arg, ast.Constant):
                if isinstance(arg.value, int) and arg.value != 0:
                    return True
            else:
                # any non-constant argument: trust it (e.g. `1 if v else 0`)
                return True
    return False


def main():
    missing = []
    for name in RIGOROUS_SCRIPTS:
        path = CODE_DIR / name
        if not path.is_file():
            missing.append(f"{name} (file not found)")
            continue
        if not has_nonzero_exit_mechanism(path.read_text()):
            missing.append(name)

    if missing:
        print("✗ FAILED: rigorous-verification scripts lacking a non-zero")
        print("  exit mechanism (sys.exit(nonzero) / assert / raise):")
        for name in missing:
            print(f"  - {name}")
        print()
        print("  README promises 'exits non-zero on violation' but these scripts")
        print("  would print '✗ FAILED' and exit 0, silently regressing in CI.")
        sys.exit(1)

    print(f"✓ VERIFIED: all {len(RIGOROUS_SCRIPTS)} rigorous-verification scripts")
    print("  have a non-zero exit mechanism.")


if __name__ == "__main__":
    main()
