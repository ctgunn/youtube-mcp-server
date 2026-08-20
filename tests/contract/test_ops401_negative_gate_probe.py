"""Intentional temporary failure used to validate OPS-401 PR enforcement."""


def test_ops401_required_tests_check_blocks_a_failing_revision() -> None:
    """Fail deliberately so the required ``tests`` check cannot pass.

    :return: This test never returns successfully while the negative test is active.
    """
    observed_quality_result = "fail"
    assert observed_quality_result == "pass"
