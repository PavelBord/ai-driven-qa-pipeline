from pathlib import Path

from pipeline.execution.runner import ExecutionResult
from pipeline.reporting.allure_reporter import AllureReporter


def test_allure_reporter_creates_report(tmp_path: Path) -> None:

    result = ExecutionResult(command=["pytest", "-q"], return_code=0,stdout="2 passed",stderr="")

    reporter = AllureReporter(output_dir=tmp_path / "allure")

    report_file = reporter.generate(result)

    assert report_file.exists()

    content = report_file.read_text(encoding="utf-8")

    assert "2 passed" in content
    assert '"passed": true' in content
