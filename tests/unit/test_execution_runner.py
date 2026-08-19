from pipeline.execution.runner import ExecutionRunner


def test_execution_runner_success() -> None:
    runner = ExecutionRunner(
        command=["python","-c","print('tests passed')"])

    result = runner.run()

    assert result.passed is True
    assert result.return_code == 0
    assert "tests passed" in result.stdout


def test_execution_runner_failure() -> None:
    runner = ExecutionRunner(command=["python","-c","raise Exception('execution failed')"])

    result = runner.run()

    assert result.passed is False
    assert result.return_code != 0
    assert "execution failed" in result.stderr