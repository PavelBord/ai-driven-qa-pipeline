from pathlib import Path

import yaml

from pipeline.pii_stage import run_pii_stage


def test_pii_stage_creates_artifacts(tmp_path: Path) -> None:
    input_file = tmp_path / "business-checklist.yaml"

    input_file.write_text(
        """
project:
  name: "Test Project"

requirements:
  - id: "AUTH-001"
    test_data:
      email: "user@example.com"
      password: "DemoPassword123"
""",
        encoding="utf-8",
    )

    output_dir = tmp_path / "artifacts"

    run_pii_stage(input_path=input_file,output_dir=output_dir)

    masked_file = output_dir / "masked-business-checklist.yaml"
    report_file = output_dir / "pii-report.json"

    assert masked_file.exists()
    assert report_file.exists()

    masked_data = yaml.safe_load(masked_file.read_text(encoding="utf-8"))

    assert (masked_data["requirements"][0]["test_data"]["email"]== "<EMAIL>")

    assert ( masked_data["requirements"][0]["test_data"]["password"]== "<PASSWORD>")