from pipeline.bug_report.generator import BugReportGenerator
from pipeline.llm.client import MockLLMClient


def test_bug_report_generator_returns_report() -> None:

    llm_response = """
{
  "title": "Pet creation returns unexpected status code",
  "severity": "high",
  "priority": "high",
  "description": "Pet creation API test failed because response status code was unexpected.",
  "steps_to_reproduce": [
    "Send POST request to /pet",
    "Check response status code"
  ],
  "expected_result": "API should return expected status code.",
  "actual_result": "API returned 200 instead of expected value."
}
"""

    generator = BugReportGenerator(MockLLMClient(llm_response))

    analysis = {
        "status": "failed",
        "error_type": "AssertionError",
        "summary": "Pet creation API returned unexpected status code.",
        "recommendation": "Check API response validation."
    }

    result = generator.generate(analysis)

    assert result.title == ("Pet creation returns unexpected status code")

    assert result.severity == "high"

    assert result.priority == "high"

    assert len(result.steps_to_reproduce) > 0