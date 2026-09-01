from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

LOG = logging.getLogger(__name__)


def format_python(path: Path) -> bool:
    """Normalize a generated file with black so PEP8 is enforced automatically.

    Returns True if formatting succeeded; black is a dev-only dependency, so a
    missing formatter degrades to a warning instead of a hard failure.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "black", "-q", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        LOG.warning("black unavailable, skipping formatting of %s: %s", path, exc)
        return False

    if result.returncode != 0:
        LOG.warning("black failed on %s: %s", path, result.stderr.strip())
        return False

    return True