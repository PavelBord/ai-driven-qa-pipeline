from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass
class ExecutionResult:
    """
    Result of automated test execution.
    """

    command: list[str]
    return_code: int
    stdout: str
    stderr: str

    @property
    def passed(self) -> bool:
        return self.return_code == 0


class ExecutionRunner:
    """
    Runs automated tests and collects execution logs.
    """

    def __init__(self,command: list[str] | None = None) -> None:self.command = command or ["pytest","-q"]

    def run(self) -> ExecutionResult:
        process = subprocess.run(self.command,capture_output=True,text=True,check=False)

        return ExecutionResult(command=self.command,return_code=process.returncode,stdout=process.stdout, stderr=process.stderr)