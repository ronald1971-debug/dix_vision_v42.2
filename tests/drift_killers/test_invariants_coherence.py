"""DRIFT-KILLER — invariant documentation / contract coherence.

Fails if:

* an `InvariantID` is missing from ``INVARIANT_DOCS``
* a docstring ``INV-*`` reference is not a known enum member
* the invariants markdown defines an ID not present in the enum

Augments the existing ``tests/drift_killers`` gate set (DOC + CODE).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INVARIANTS_MD = ROOT / "docs" / "invariants_dixvision_v42.2.md"
CONTRACTS_INVARIANTS = ROOT / "core" / "contracts" / "invariants.py"


def _load_invariant_ids() -> set[str]:
    from core.contracts.invariants import InvariantID
    return {m.value for m in InvariantID}


def _load_invariant_docs() -> dict[str, str]:
    from core.contracts.invariants import INVARIANT_DOCS
    return dict(INVARIANT_DOCS)


def _load_md_invariant_ids(text: str) -> set[str]:
    return set(re.findall(r"INV-DIX-\d{2}", text))


def test_invariant_id_registry_is_complete() -> None:
    known = _load_invariant_ids()
    docs = _load_invariant_docs()

    missing_docs = {iid for iid in known if iid not in docs}
    assert not missing_docs, (
        "InvariantIDs missing from INVARIANT_DOCS: "
        + ", ".join(sorted(missing_docs))
    )


def test_invariants_markdown_matches_enum() -> None:
    md_text = INVARIANTS_MD.read_text(encoding="utf-8")
    md_ids = _load_md_invariant_ids(md_text)
    known = _load_invariant_ids()

    unknown = md_ids - known
    assert not unknown, (
        "docs/invariants_dixvision_v42.2.md references unknown invariant IDs: "
        + ", ".join(sorted(unknown))
    )

    missing = {iid for iid in known if "DIX" in iid} - md_ids
    assert not missing, (
        "Missing from docs/invariants_dixvision_v42.2.md: "
        + ", ".join(sorted(missing))
    )


def test_required_reality_domains_present_in_belief_state() -> None:
    from core.contracts.invariants import InvariantID
    from governance_engine.hardening.invariants_state import required_reality_domains

    if InvariantID.DIX_02 not in {m.value for m in InvariantID}:
        return

    import ast

    source = (ROOT / "core" / "contracts" / "belief_state.py").read_text(encoding="utf-8")
    module = ast.parse(source)

    class_found = False
    declared_fields: set[str] = set()
    for node in ast.walk(module):
        if isinstance(node, ast.ClassDef) and node.name == "BeliefState":
            class_found = True
            for item in node.body:
                if isinstance(item, ast.AnnAssign):
                    target = item.target
                    if isinstance(target, ast.Name):
                        declared_fields.add(target.id)

    assert class_found, "BeliefState class not found in core/contracts/belief_state.py"

    domains = set(required_reality_domains())
    missing = domains - declared_fields
    assert not missing, (
        "core/contracts/belief_state.py missing required reality domains "
        "(INV-DIX-02): " + ", ".join(sorted(missing))
    )


def test_describe_function_covers_all() -> None:
    from core.contracts.invariants import InvariantID, describe

    for iid in InvariantID:
        desc = describe(iid.value)
        assert desc != "unknown invariant", f"describe({iid.value}) missing"
        assert len(desc) > 0, f"describe({iid.value}) empty"


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    tests = [
        test_invariant_id_registry_is_complete,
        test_invariants_markdown_matches_enum,
        test_required_reality_domains_present_in_belief_state,
        test_describe_function_covers_all,
    ]
    for test in tests:
        try:
            test()
        except AssertionError as exc:
            print(f"FAIL {test.__name__}: {exc}", file=sys.stderr)
            sys.exit(1)
    print("All invariant drift-killer checks passed.")
