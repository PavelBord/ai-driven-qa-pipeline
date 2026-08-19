from pathlib import Path

from pipeline.checklist_loader import load_checklist


def test_load_business_checklist() -> None:
    checklist_path = Path("input/business-checklist.yaml")

    checklist = load_checklist(checklist_path)

    assert checklist.project["name"] == "AI-driven QA Demo"
    assert len(checklist.requirements) == 5
    assert checklist.requirements[0].id == "AUTH-001"