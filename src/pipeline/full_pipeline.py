from __future__ import annotations

import json
from pathlib import Path

import yaml

from pipeline.code_reviewer.code_reviewer import CodeReviewer
from pipeline.codegen.code_generator import CodeGenerator
from pipeline.codegen.file_writer import TestFileWriter
from pipeline.llm.ollama_client import OllamaClient
from pipeline.pii.pii_stage import run_pii_stage
from pipeline.scenario.scenario_generation import ScenarioGenerator


def main() -> None:

    input_file = Path(
        "input/business-checklist.yaml"
    )

    pii_dir = Path(
        "artifacts/pii"
    )

    run_pii_stage(
        input_path=input_file,
        output_dir=pii_dir,
    )


    masked_file = pii_dir / (
        "masked-business-checklist.yaml"
    )

    with masked_file.open(
        encoding="utf-8"
    ) as file:

        checklist = yaml.safe_load(
            file
        )


    llm_client = OllamaClient()


    scenario_generator = ScenarioGenerator(
        llm_client
    )

    contract = scenario_generator.generate(
        checklist
    )


    scenario_file = Path(
        "artifacts/scenarios/test-scenarios.json"
    )

    scenario_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    scenario_file.write_text(
        json.dumps(
            contract,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


    code_generator = CodeGenerator(
        llm_client
    )

    reviewer = CodeReviewer(
        llm_client
    )

    writer = TestFileWriter()


    generated_dir = Path(
        "artifacts/generated"
    )

    review_dir = Path(
        "artifacts/code-review"
    )


    for test_case in contract["test_cases"]:

        code = code_generator.generate(
            {
                "test_cases": [
                    test_case
                ]
            }
        )


        review = reviewer.review(
            code
        )


        review_file = review_dir / (
            f"{test_case['id']}.json"
        )

        review_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )


        review_file.write_text(
            json.dumps(
                review,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )


        test_name = test_case["id"].replace(
            "-",
            "_",
        )


        test_file = generated_dir / (
            f"test_{test_name}.py"
        )


        writer.save(
            code=code,
            path=test_file,
        )


    print(
        f"Created: {scenario_file}"
    )

    print(
        f"Generated tests: {generated_dir}"
    )

    print(
        f"Code review: {review_dir}"
    )


if __name__ == "__main__":
    main()