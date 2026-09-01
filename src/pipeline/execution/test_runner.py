from __future__ import annotations

import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class ExecutionResult:
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    duration_seconds: float = 0.0
    results: dict[str, str] = field(default_factory=dict)

    def failed_test_names(self) -> list[str]:
        return sorted(
            name
            for name, status in self.results.items()
            if status in {"failed", "error"}
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class TestRunner:
    """Run generated pytest tests and parse JUnit XML output."""

    __test__ = False

    def __init__(self, python: str = sys.executable) -> None:
        self.python = python

    def run(self, test_dir: Path, junit_path: Path) -> ExecutionResult:
        test_dir.mkdir(parents=True, exist_ok=True)
        junit_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            self.python,
            "-m",
            "pytest",
            "-q",
            "--no-header",
            "--junitxml",
            str(junit_path),
            "-p",
            "no:cacheprovider",
        ]

        if os.environ.get("QA_SANDBOX", "1") != "0":
            cmd += ["-p", "pipeline.execution.sandbox"]

        cmd.append(str(test_dir))

        subprocess.run(cmd, capture_output=True, text=True, check=False)

        return self._parse_junit(junit_path)

    @staticmethod
    def _parse_junit(junit_path: Path) -> ExecutionResult:
        if not junit_path.exists():
            return ExecutionResult()

        root = ET.parse(junit_path).getroot()

        result = ExecutionResult(duration_seconds=0.0)
        duration = root.get("time", "0.0")
        try:
            result.duration_seconds = float(duration)
        except ValueError:
            result.duration_seconds = 0.0

        for suite in root.iter("testsuite"):
            suite_tests = int(suite.get("tests", 0))
            suite_errors = int(suite.get("errors", 0))
            suite_failures = int(suite.get("failures", 0))
            suite_skipped = int(suite.get("skipped", 0))
            result.total += suite_tests
            result.passed += suite_tests - suite_errors - suite_failures - suite_skipped
            result.failed += suite_failures
            result.errors += suite_errors
            result.skipped += suite_skipped

        for case in root.iter("testcase"):
            status = "passed"
            for child in case:
                if child.tag in {"failure", "error"}:
                    status = "failed"
                elif child.tag == "skipped":
                    status = "skipped"
            name = case.get("name")
            if name:
                result.results[name] = status

        return result

    @staticmethod
    def write_summary(result: ExecutionResult, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(result.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return path