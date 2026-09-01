from __future__ import annotations

import sys

from pipeline.execution.test_runner import TestRunner

JUNIT_XML = """<?xml version="1.0" encoding="utf-8"?>
<testsuites time="1.25">
  <testsuite name="pytest" tests="3" failures="1" errors="0" skipped="1" time="1.25">
    <testcase classname="test_a" name="test_TC_001" time="0.1"/>
    <testcase classname="test_a" name="test_TC_002" time="0.2">
      <failure message="assert False">traceback</failure>
    </testcase>
    <testcase classname="test_a" name="test_TC_003" time="0.0">
      <skipped message="skip"/>
    </testcase>
  </testsuite>
</testsuites>
"""


def test_parse_junit_counts() -> None:
    path = _write_tmp_xml()

    result = TestRunner._parse_junit(path)

    assert result.total == 3
    assert result.passed == 1
    assert result.failed == 1
    assert result.skipped == 1
    assert result.errors == 0
    assert result.results["test_TC_001"] == "passed"
    assert result.results["test_TC_002"] == "failed"
    assert result.results["test_TC_003"] == "skipped"
    assert result.failed_test_names() == ["test_TC_002"]


def test_duration_parsing() -> None:
    result = TestRunner._parse_junit(_write_tmp_xml())
    assert result.duration_seconds == 1.25


def test_run_generated_tests(tmp_path) -> None:
    test_dir = tmp_path / "generated"
    test_dir.mkdir()
    (test_dir / "test_x.py").write_text(
        "def test_pass():\n    assert True\n\n"
        "def test_fail():\n    assert False\n",
        encoding="utf-8",
    )
    junit = tmp_path / "test-results.xml"

    runner = TestRunner(python=sys.executable)
    result = runner.run(test_dir, junit)

    assert result.total == 2
    assert result.passed == 1
    assert result.failed == 1
    assert result.failed_test_names() == ["test_fail"]


def _write_tmp_xml():
    from pathlib import Path

    tmp = Path(__import__("tempfile").mkdtemp())
    path = tmp / "junit.xml"
    path.write_text(JUNIT_XML, encoding="utf-8")
    return path