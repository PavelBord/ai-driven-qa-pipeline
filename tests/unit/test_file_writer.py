from pathlib import Path

from pipeline.test_generator.file_writer import TestFileWriter


def test_saves_generated_test_file(tmp_path: Path) -> None:

    file_path = (tmp_path /"generated_tests" /"test_auth.py")

    code = """
def test_login():
    assert True
"""

    result = TestFileWriter().save(code,file_path)

    assert result.exists()

    assert (result.read_text(encoding="utf-8")== code)