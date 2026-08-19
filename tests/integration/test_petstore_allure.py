from pathlib import Path

from pipeline.execution.runner import ExecutionRunner
from pipeline.reporting.allure_reporter import AllureReporter


def test_petstore_allure_report() -> None:

    runner = ExecutionRunner(
        [
            "pytest",
            "-q",
            "tests/api/test_petstore_api.py",
        ]
    )

    result = runner.run()

    reporter = AllureReporter(output_dir=Path("artifacts/allure"))

    report_file = reporter.generate(result)

    assert report_file.exists()

    assert "execution-result.json" in str(report_file)