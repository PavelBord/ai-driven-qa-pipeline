from pipeline.code_review.reviewer import CodeReviewer
from pipeline.llm.client import MockLLMClient


def test_code_reviewer_returns_review() -> None:

    llm_response = """
    {
      "approved": true,
      "score": 9,
      "issues": [],
      "recommendation": "Code quality is good."
    }
    """

    reviewer = CodeReviewer(MockLLMClient(llm_response))

    result = reviewer.review(
        """
        def test_login():
            response = login()
            assert response.status == 200
        """
    )

    assert result.approved is True
    assert result.score == 9
    assert len(result.issues) == 0
    assert (result.recommendation== "Code quality is good.")