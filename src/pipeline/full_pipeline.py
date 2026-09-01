from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from pipeline.bug_report.generator import BugReportGenerator
from pipeline.code_reviewer.code_reviewer import CodeReviewer
from pipeline.codegen.code_generator import CodeGenerator
from pipeline.codegen.code_validator import CodeValidationError, CodeValidator
from pipeline.codegen.file_writer import TestFileWriter
from pipeline.config import (
    BASE_DIR,
    BUG_REPORT_DIR,
    EXECUTION_DIR,
    GENERATED_DIR,
    PAGES_DIR,
    PII_DIR,
    REVIEW_DIR,
    SCENARIOS_DIR,
)
from pipeline.execution.test_runner import TestRunner
from pipeline.formatting import format_python
from pipeline.llm.mock_client import MockLLMClient
from pipeline.llm.ollama_client import OllamaClient
from pipeline.page_objects.page_generator import PageGenerator
from pipeline.pii.pii_stage import run_pii_stage
from pipeline.reporting import clear_artifacts, write_manifest
from pipeline.scenario.scenario_generation import ScenarioGenerator

LOG = logging.getLogger(__name__)

INPUT_FILE = BASE_DIR / "input" / "demo-web-shop-checklist.yaml"


def setup_logging() -> None:
    level = logging.DEBUG if os.getenv("QA_DEBUG") else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
    )


def get_llm_client() -> Any:

    if os.getenv("CI"):
        return MockLLMClient()

    return OllamaClient()


def _test_function_name(test_case_id: str) -> str:
    return f"test_{test_case_id.replace('-', '_')}"


def _save_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _generate_bug_report(
    bug_report_generator: BugReportGenerator,
    test_case: dict[str, Any],
    conclusion: dict[str, Any],
) -> None:
    try:
        report = bug_report_generator.generate(
            {
                "test_case": test_case,
                "conclusion": conclusion,
            }
        )
        BugReportGenerator.save(report, test_case["id"])
        LOG.info("Bug report created for %s (%s)", test_case["id"], conclusion.get("kind"))
    except (json.JSONDecodeError, ValidationError) as exc:
        LOG.warning("Skipping bug report for %s: %s", test_case["id"], exc)


def validate_checklist(checklist: Any) -> None:
    if not isinstance(checklist, dict):
        raise TypeError("Checklist must be a mapping")
    expected = {"application", "pages", "requirements"}
    missing = expected - set(checklist.keys())
    if missing:
        raise ValueError(f"Checklist is missing required sections: {sorted(missing)}")


def generate_and_review_tests(
    llm_client: Any,
    contract: dict[str, Any],
    bug_report_generator: BugReportGenerator,
) -> None:
    code_generator = CodeGenerator(llm_client)
    reviewer = CodeReviewer(llm_client)
    writer = TestFileWriter()

    for test_case in contract["test_cases"]:
        test_id = test_case["id"]
        code = code_generator.generate({"test_cases": [test_case]})

        review = reviewer.review(code)

        review_file = REVIEW_DIR / f"{test_id}.json"
        _save_json(review, review_file)

        if review.get("status") == "failed":
            _generate_bug_report(
                bug_report_generator,
                test_case,
                {"kind": "code_review", "review": review},
            )

        try:
            CodeValidator.validate(code)
        except CodeValidationError as exc:
            LOG.warning("SKIP %s (validation): %s", test_id, exc)
            _generate_bug_report(
                bug_report_generator,
                test_case,
                {"kind": "code_validation", "issues": str(exc)},
            )
            continue

        writer.save(code=code, path=GENERATED_DIR / f"{_test_function_name(test_id)}.py")
        format_python(GENERATED_DIR / f"{_test_function_name(test_id)}.py")
        LOG.info("Generated %s/%s.py", GENERATED_DIR, _test_function_name(test_id))


def run_execution_stage(
    contract: dict[str, Any],
    bug_report_generator: BugReportGenerator,
) -> None:
    test_cases = contract.get("test_cases", [])
    if not test_cases:
        LOG.info("Execution skipped: no generated tests")
        return

    junit_path = EXECUTION_DIR / "test-results.xml"
    runner = TestRunner()
    result = runner.run(GENERATED_DIR, junit_path)

    summary_path = EXECUTION_DIR / "execution-summary.json"
    TestRunner.write_summary(result, summary_path)

    LOG.info(
        "Execution: total=%s passed=%s failed=%s skipped=%s errors=%s (%.2fs)",
        result.total,
        result.passed,
        result.failed,
        result.skipped,
        result.errors,
        result.duration_seconds,
    )
    LOG.info("Execution summary: %s", summary_path)

    failed_names = result.failed_test_names()

    for test_case in test_cases:
        if _test_function_name(test_case["id"]) in failed_names:
            _generate_bug_report(
                bug_report_generator,
                test_case,
                {"kind": "test_execution", "status": "failed"},
            )


def main() -> None:
    setup_logging()
    clear_artifacts()

    llm_client = get_llm_client()

    run_pii_stage(
        input_path=INPUT_FILE,
        output_dir=PII_DIR,
    )

    masked_file = PII_DIR / "masked-business-checklist.yaml"

    with masked_file.open(encoding="utf-8") as file:
        checklist = yaml.safe_load(file)

    validate_checklist(checklist)

    page_generator = PageGenerator(llm_client)
    pages = checklist.get("pages", [])
    for page_data in pages:
        page_code = page_generator.generate(page_data)
        page_generator.save(code=page_code, page_name=page_data["page_name"])

    contract = ScenarioGenerator(llm_client).generate(checklist)

    scenario_file = SCENARIOS_DIR / "test-scenarios.json"
    _save_json(contract, scenario_file)

    bug_report_generator = BugReportGenerator(llm_client)

    generate_and_review_tests(llm_client, contract, bug_report_generator)

    manifest_path = write_manifest(llm_client)
    LOG.info("Created: %s", scenario_file)
    LOG.info("Generated pages: %s", PAGES_DIR)
    LOG.info("Generated tests: %s", GENERATED_DIR)
    LOG.info("Code review: %s", REVIEW_DIR)
    LOG.info("Bug reports: %s", BUG_REPORT_DIR)
    LOG.info("Manifest: %s", manifest_path)

    run_execution_stage(contract, bug_report_generator)


if __name__ == "__main__":
    main()