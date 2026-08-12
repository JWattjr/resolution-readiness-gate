import ast
from pathlib import Path


def test_consensus_closures_do_not_capture_contract_storage():
    tree = ast.parse(Path("contracts/ResolutionReadinessGate.py").read_text(encoding="utf-8"))
    violations = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and node.name in ("leader_fn", "validator_fn")
        and any(isinstance(child, ast.Name) and child.id == "self" for child in ast.walk(node))
    ]
    assert violations == []
