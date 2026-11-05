from hypothesis import given, strategies as st
from mobile_data_plan import parse_plan, usage_average, payable_bill
import pytest


def check_no_unexpected_crash(function, value):
    try:
        result = function(value)
        return result
    except ValueError:
        return None
    except Exception as exc:
        pytest.fail(
            f"Unexpected exception: {type(exc).__name__}: {exc}"
        )


@given(st.text() | st.none())
def test_parse_plan_no_crash(s):
    check_no_unexpected_crash(parse_plan, s)


@given(st.text() | st.none())
def test_usage_average_no_crash(s):
    check_no_unexpected_crash(usage_average, s)


@given(st.text() | st.none())
def test_payable_bill_no_crash(s):
    check_no_unexpected_crash(payable_bill, s)