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
  - a `raise` statement,

AND, if the chosen mechanism is `sys.exit`, that `sys` is actually imported
at module level (`import sys` or `from sys import exit`). The latter catches
the silent-crash failure mode where `sys.exit(1)` is written but `sys` is
never imported: the violation path then raises `NameError` / `AttributeError`
instead of performing a controlled exit. Exit status is incidentally
non-zero in that case, but a future maintainer wrapping `main()` in
`try/except` would silently turn it into exit 0.

This is a necessary condition, not a sufficient one: the test does not
verify the exit path is actually reachable from a real violation. But it
catches the present concrete bug class (script has no exit mechanism at
all, or has `sys.exit` without `import sys`) and any future regression of
the same shape.

Run with:  python3 meta_test_exit_convention.py
"""

import ast
import pathlib
import sys

CODE_DIR = pathlib.Path(__file__).resolve().parent

# Scripts the README's "Rigorous verification" table promises will exit
# non-zero on violation. obstr_factor_complexity.py is intentionally NOT in
# this list - it is heuristic-only (see review M-02 of the tenth pass).
RIGOROUS_SCRIPTS = [
    "atomic_anchor_verification.py",
    "atomic_g0_early_stop_check.py",
    "count_obstructions.py",
    "factor_complexity_construction.py",
    "independent_enumeration.py",
    "iso_synchronisation_verification.py",
    "lift_lemma_test.py",
    "lift_symmetry_verification.py",
    "tplus_bijection_verification.py",
    "x_invariant_bidirectional.py",
    "x_invariant_non_obstructions.py",
    # Shift-index window (sec:shift-window): depth bound and its corollary.
    "signfree_identity_check.py",
    "depth_bound_threshold.py",
    "depth_closed_form.py",
    "depth_carry_automaton_k2.py",
    "depth_carry_automaton_neg.py",
    "depth_carry_statespace.py",
    "depth_dfs_tails.py",
    "shift_index_window_check.py",
]


def _module_imports_sys(tree: ast.AST) -> bool:
    """Return True iff the module's top level contains `import sys` (or
    aliases) or `from sys import ...`."""
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "sys":
                    return True
        elif isinstance(node, ast.ImportFrom):
            if node.module == "sys":
                return True
    return False


def classify_exit_mechanism(source: str):
    """Return (has_mechanism, uses_sys_exit, imports_sys).

    has_mechanism: True iff the source contains sys.exit(<nonzero>), assert,
                   or raise.
    uses_sys_exit: True iff sys.exit(<nonzero or non-constant>) appears.
    imports_sys:   True iff the module imports sys at top level.
    """
    tree = ast.parse(source)
    imports_sys = _module_imports_sys(tree)
    uses_sys_exit = False
    has_assert_or_raise = False
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assert, ast.Raise)):
            has_assert_or_raise = True
            continue
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
                    uses_sys_exit = True
            else:
                # any non-constant argument: trust it (e.g. `1 if v else 0`)
                uses_sys_exit = True
    has_mechanism = uses_sys_exit or has_assert_or_raise
    return has_mechanism, uses_sys_exit, imports_sys


def main():
    no_mechanism = []
    sys_exit_without_import = []
    for name in RIGOROUS_SCRIPTS:
        path = CODE_DIR / name
        if not path.is_file():
            no_mechanism.append(f"{name} (file not found)")
            continue
        has_mech, uses_sys_exit, imports_sys = classify_exit_mechanism(
            path.read_text()
        )
        if not has_mech:
            no_mechanism.append(name)
        elif uses_sys_exit and not imports_sys:
            sys_exit_without_import.append(name)

    failed = False
    if no_mechanism:
        failed = True
        print("✗ FAILED: rigorous-verification scripts lacking a non-zero")
        print("  exit mechanism (sys.exit(nonzero) / assert / raise):")
        for name in no_mechanism:
            print(f"  - {name}")
        print()
        print("  README promises 'exits non-zero on violation' but these scripts")
        print("  would print '✗ FAILED' and exit 0, silently regressing in CI.")
    if sys_exit_without_import:
        failed = True
        print("✗ FAILED: rigorous-verification scripts call sys.exit but do not")
        print("  import sys:")
        for name in sys_exit_without_import:
            print(f"  - {name}")
        print()
        print("  On a real violation the script would crash with NameError /")
        print("  AttributeError instead of performing a controlled non-zero exit.")
        print("  Add `import sys` at the top of each file.")

    if failed:
        sys.exit(1)

    print(f"✓ VERIFIED: all {len(RIGOROUS_SCRIPTS)} rigorous-verification scripts")
    print("  have a non-zero exit mechanism and (if they use sys.exit) import sys.")


if __name__ == "__main__":
    main()
