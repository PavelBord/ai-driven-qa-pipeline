from pipeline.analysis.log_analyzer import LogAnalyzer
from pipeline.llm.client import MockLLMClient


def test_log_analyzer_returns_structured_result() -> None:

    llm_response = """
    {
      "status": "failed",
      "error_type": "AssertionError",
      "summary": "Authentication test failed.",
      "recommendation": "Check authentication logic."
    }
    """

    analyzer = LogAnalyzer(MockLLMClient(llm_response))

    result = analyzer.analyze(
"""
        FAILED test_login
        AssertionError:
        Expected success but got failure
        """
    )

    assert result.status == "failed"
    assert result.error_type == "AssertionError"
    assert (result.summary== "Authentication test failed.")

    assert (result.recommendation== "Check authentication logic.")