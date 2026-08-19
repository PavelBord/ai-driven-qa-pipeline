from pipeline.bug_report.generator import BugReportGenerator
from pipeline.llm.client import MockLLMClient


def test_bug_report_generator_returns_report() -> None:

    llm_response = """
    {
      "title": "Authentication test failed",
      "severity": "high",
      "priority": "high",
      "description": "Login scenario failed during execution.",
      "steps_to_reproduce": [
        "Run authentication test",
        "Provide valid credentials",
        "Execute login"
      ],
      "expected_result": "User should be authenticated.",
      "actual_result": "Authentication failed."
    }
    """

    generator = BugReportGenerator(MockLLMClient(llm_response))

    report = generator.generate(
        {
            "status": "failed",
            "error_type": "AssertionError",
            "summary": "Authentication test failed",
            "recommendation": "Check login logic",
        }
    )

    assert (report.title== "Authentication test failed")

    assert report.severity == "high"
    assert report.priority == "high"

    assert len(report.steps_to_reproduce) == 3

    assert (report.actual_result== "Authentication failed.")