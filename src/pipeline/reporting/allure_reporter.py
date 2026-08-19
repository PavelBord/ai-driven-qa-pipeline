from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pipeline.execution.runner import ExecutionResult


class AllureReporter:

    def __init__(self,output_dir: Path = Path("artifacts/allure")) -> None:
        self.output_dir = output_dir


    def generate(self,result: ExecutionResult,analysis: dict[str, Any] | None = None,bug_report: dict[str, Any] | None = None) -> Path:

        self.output_dir.mkdir(parents=True,exist_ok=True)

        report_file = (self.output_dir/ "execution-result.json")

        data = {
            "execution": {
                "command": result.command,
                "passed": result.passed,
                "return_code": result.return_code,
            },
            "logs": {
                "stdout": result.stdout,
                "stderr": result.stderr,
            },
            "ai_analysis": analysis,
            "bug_report": bug_report,
        }

        report_file.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding="utf-8",)

        return report_file