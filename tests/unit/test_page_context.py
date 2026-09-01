from unittest.mock import patch

from pipeline.page_context import load_pages_context


def test_load_pages_context():
    """Тестируем загрузку контекста страниц."""
    result = load_pages_context()
    assert result == "[]"


def test_load_pages_context_logging():
    """Тестируем логирование в load_pages_context."""
    with patch("pipeline.page_context.logger") as mock_logger:
        load_pages_context()
        mock_logger.info.assert_called_once_with("Loading pages context")
