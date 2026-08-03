"""Chapter 45: a sandboxed inspect-patch-test Coding Agent MVP."""

from __future__ import annotations

import ast
import difflib
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory


SOURCE = '''def final_price(subtotal: float, discount: float) -> float:\n    """Return subtotal after an absolute discount."""\n    return subtotal + discount\n'''
TEST = '''import unittest\nfrom pricing import final_price\n\nclass PricingTest(unittest.TestCase):\n    def test_discount_is_subtracted(self):\n        self.assertEqual(final_price(100.0, 15.0), 85.0)\n\nif __name__ == "__main__":\n    unittest.main()\n'''


@dataclass(frozen=True)
class ChangeRequest:
    objective: str
    target: str
    old: str
    new: str


def resolve_inside(workspace: Path, relative: str) -> Path:
    target = (workspace / relative).resolve()
    if workspace.resolve() not in target.parents:
        raise PermissionError("target escapes the sandbox")
    if target.suffix != ".py":
        raise PermissionError("only Python source files are allowlisted")
    return target


def inspect_source(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    return {"path": path.name, "sha_like_length": len(text), "functions": functions, "content": text}


def propose_patch(source: str, change: ChangeRequest) -> tuple[str, str]:
    if source.count(change.old) != 1:
        raise ValueError("patch anchor must match exactly once")
    updated = source.replace(change.old, change.new, 1)
    ast.parse(updated)
    diff = "".join(
        difflib.unified_diff(
            source.splitlines(keepends=True),
            updated.splitlines(keepends=True),
            fromfile=f"a/{change.target}",
            tofile=f"b/{change.target}",
        )
    )
    return updated, diff


def run_tests(workspace: Path) -> dict:
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "-v"],
        cwd=workspace,
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )
    return {
        "command": [sys.executable, "-m", "unittest", "-v"],
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def run_agent(workspace: Path, change: ChangeRequest) -> dict:
    target = resolve_inside(workspace, change.target)
    inspection = inspect_source(target)
    before_tests = run_tests(workspace)
    updated, diff = propose_patch(inspection["content"], change)
    target.write_text(updated, encoding="utf-8")
    after_tests = run_tests(workspace)
    if after_tests["returncode"] != 0:
        target.write_text(inspection["content"], encoding="utf-8")
        raise RuntimeError("candidate patch failed tests and was rolled back")
    return {
        "status": "ready_for_review",
        "objective": change.objective,
        "inspection": {key: value for key, value in inspection.items() if key != "content"},
        "baseline_test_returncode": before_tests["returncode"],
        "patch": diff,
        "verification": after_tests,
        "commit_created": False,
        "approval_required": True,
    }


def main() -> None:
    with TemporaryDirectory(prefix="coding-agent-") as directory:
        workspace = Path(directory)
        (workspace / "pricing.py").write_text(SOURCE, encoding="utf-8")
        (workspace / "test_pricing.py").write_text(TEST, encoding="utf-8")
        change = ChangeRequest(
            objective="Fix discount calculation without changing the public API",
            target="pricing.py",
            old="return subtotal + discount",
            new="return subtotal - discount",
        )
        print(json.dumps(run_agent(workspace, change), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
