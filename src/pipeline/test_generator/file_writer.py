from pathlib import Path


class TestFileWriter:

    def save(self,code: str,path: Path) -> Path:

        path.parent.mkdir(parents=True,exist_ok=True)

        path.write_text(code,encoding="utf-8")

        return path