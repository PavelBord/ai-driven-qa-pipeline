from pipeline.analysis.log_analyzer import LogAnalyzer
from pipeline.llm.client import MockLLMClient


def test_failed_test_log_analysis() -> None:

    llm_response = """
{
  "status": "failed",
  "error_type": "AssertionError",
  "summary": "Pet creation API returned unexpected status code.",
  "recommendation": "Check API response validation."
}
"""

    analyzer = LogAnalyzer(MockLLMClient(llm_response))

    result = analyzer.analyze(
        """
        FAILED test_create_pet

        AssertionError:
        assert 200 == 500

        Expected server error but received success response.
        """
    )

    assert result.status == "failed"

    assert (result.error_type == "AssertionError")

    assert ("Pet creation"in result.summary)