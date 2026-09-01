from unittest.mock import Mock, patch

import pytest

from pipeline.codegen.code_generator import CodeGenerator


def test_code_generator_initialization():
    """Тестируем инициализацию генератора."""
    mock_client = Mock()
    generator = CodeGenerator(mock_client)
    assert generator.llm_client == mock_client


def test_code_generator_generate_success():
    """Тестируем успешную генерацию."""
    mock_client = Mock()
    mock_client.generate.return_value = "generated_code"
    generator = CodeGenerator(mock_client)

    data = {"test_cases": [{"name": "test1"}]}

    result = generator.generate(data)
    assert result == "generated_code"
    mock_client.generate.assert_called_once()


def test_code_generator_missing_test_cases():
    """Тестируем обработку отсутствующих тестовых случаев."""
    mock_client = Mock()
    generator = CodeGenerator(mock_client)

    with pytest.raises(ValueError, match="test_cases must be provided in data"):
        generator.generate({})


def test_code_generator_empty_test_cases():
    """Тестируем обработку пустых тестовых случаев."""
    mock_client = Mock()
    generator = CodeGenerator(mock_client)

    with pytest.raises(ValueError, match="test_cases must be a non-empty list"):
        generator.generate({"test_cases": []})


def test_code_generator_generate_with_pages():
    """Тестируем генерацию с переданным контекстом страниц."""
    mock_client = Mock()
    mock_client.generate.return_value = "generated_code_with_pages"
    generator = CodeGenerator(mock_client)

    data = {"test_cases": [{"name": "test1"}]}
    pages = "mock_pages_context"

    result = generator.generate(data, pages)
    assert result == "generated_code_with_pages"


def test_code_generator_empty_result():
    """Тестируем обработку пустого результата от LLM."""
    mock_client = Mock()
    mock_client.generate.return_value = ""
    generator = CodeGenerator(mock_client)

    data = {"test_cases": [{"name": "test1"}]}

    with pytest.raises(RuntimeError, match="LLM returned empty result"):
        generator.generate(data)


def test_code_generator_invalid_data_type():
    """Тестируем обработку неверного типа данных."""
    mock_client = Mock()
    generator = CodeGenerator(mock_client)

    with pytest.raises(TypeError, match="Data must be a dictionary"):
        generator.generate("not_a_dict")


def test_code_generator_prompt_loading_success():
    """Тестируем успешную загрузку промпта."""
    with patch(
        "pipeline.codegen.code_generator.PROMPT_PATH"
    ) as mock_prompt_path:
        mock_prompt_path.read_text.return_value = (
            "test prompt {test_case} {pages}"
        )
        result = CodeGenerator._load_prompt()
        assert result == "test prompt {test_case} {pages}"


def test_code_generator_prompt_loading_failure():
    """Тестируем обработку ошибки загрузки промпта."""
    with (
        patch(
            "pipeline.codegen.code_generator.PROMPT_PATH"
        ) as mock_prompt_path,
        pytest.raises(RuntimeError, match="Required prompt file not found"),
    ):
        mock_prompt_path.read_text.side_effect = FileNotFoundError(
            "File not found"
        )
        CodeGenerator._load_prompt()
