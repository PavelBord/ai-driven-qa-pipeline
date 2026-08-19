from pipeline.execution.runner import ExecutionRunner


def test_petstore_execution_runner() -> None:

    runner = ExecutionRunner(
        [
            "pytest",
            "-q",
            "tests/api/test_petstore_api.py",
        ]
    )

    result = runner.run()

    assert result.return_code == 0

    assert result.passed is True

    assert "passed" in result.stdout