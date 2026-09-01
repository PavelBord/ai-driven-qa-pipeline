from unittest.mock import Mock

from pipeline.codegen.code_generator import CodeGenerator


def test_code_generator_complex_data():
    """Тестируем генерацию с комплексными данными."""
    mock_client = Mock()
    mock_client.generate.return_value = "complex_generated_code"
    generator = CodeGenerator(mock_client)

    complex_data = {
        "test_cases": [{
            "name": "complex_test",
            "steps": ["step1", "step2"],
            "expected": "result",
            "tags": ["tag1", "tag2"]
        }],
        "metadata": {"version": "1.0"}
    }

    result = generator.generate(complex_data)
    assert result == "complex_generated_code"


def test_code_generator_special_characters():
    """Тестируем обработку специальных символов."""
    mock_client = Mock()
    mock_client.generate.return_value = "code_with_special_chars"
    generator = CodeGenerator(mock_client)

    data_with_special = {
        "test_cases": [{
            "name": "test with 'quotes' and \"double quotes\"",
            "steps": ["step with\nnewlines", "step with\ttabs"]
        }]
    }

    result = generator.generate(data_with_special)
    assert result == "code_with_special_chars"


def test_code_generator_none_pages():
    """Тестируем генерацию с None pages."""
    mock_client = Mock()
    mock_client.generate.return_value = "code_with_none_pages"
    generator = CodeGenerator(mock_client)

    data = {"test_cases": [{"name": "test"}]}

    result = generator.generate(data, None)
    assert result == "code_with_none_pages"
