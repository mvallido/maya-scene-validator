"""Unit tests for the TestCase base class logic."""
import sys
import pytest

# conftest.py has already injected maya mocks — safe to import now
from cz_validation.test_cases.test_case import TestCase


class _PassingTest(TestCase):
    """Minimal concrete subclass — execute() returns True, no Maya calls."""
    NAME = "Passing Test"
    DESCRIPTION = "Always passes"
    CATEGORY = "Test"

    def execute(self):
        return True


class _FailingTest(TestCase):
    """Minimal concrete subclass — execute() appends an error and returns False."""
    NAME = "Failing Test"
    DESCRIPTION = "Always fails"
    CATEGORY = "Test"

    def execute(self):
        self._errors.append("bad_node")
        return False


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------

def test_initial_state():
    tc = _PassingTest()
    assert tc._run_completed is False
    assert tc._passed is False
    assert tc._errors == []
    assert tc.has_run_completed() is False
    assert tc.has_passed() is False


# ---------------------------------------------------------------------------
# run_test()
# ---------------------------------------------------------------------------

def test_run_test_sets_completed():
    tc = _PassingTest()
    tc.run_test()
    assert tc.has_run_completed() is True


def test_run_test_returns_true_on_pass():
    tc = _PassingTest()
    result = tc.run_test()
    assert result is True
    assert tc.has_passed() is True


def test_run_test_returns_false_on_fail():
    tc = _FailingTest()
    result = tc.run_test()
    assert result is False
    assert tc.has_passed() is False


def test_base_execute_returns_false():
    """Base TestCase.execute() always fails and appends an error."""
    tc = TestCase()
    result = tc.run_test()
    assert result is False
    assert len(tc._errors) == 1


# ---------------------------------------------------------------------------
# reset()
# ---------------------------------------------------------------------------

def test_reset_clears_state():
    tc = _FailingTest()
    tc.run_test()
    assert tc.has_run_completed() is True

    tc.reset()
    assert tc._run_completed is False
    assert tc._passed is False
    assert tc._errors == []
    assert tc.has_run_completed() is False
    assert tc.has_passed() is False


def test_run_test_calls_reset_internally():
    """run_test() resets before executing — errors from a previous run are cleared."""
    tc = _FailingTest()
    tc.run_test()
    assert len(tc._errors) == 1
    tc.run_test()
    assert len(tc._errors) == 1  # still 1, not 2


# ---------------------------------------------------------------------------
# formatted_results()
# ---------------------------------------------------------------------------

def test_formatted_results_not_run():
    tc = _PassingTest()
    result = tc.formatted_results()
    assert result.startswith("NOT RUN:")


def test_formatted_results_passed():
    tc = _PassingTest()
    tc.run_test()
    result = tc.formatted_results()
    assert result.startswith("PASSED:")


def test_formatted_results_failed_contains_error():
    tc = _FailingTest()
    tc.run_test()
    result = tc.formatted_results()
    assert result.startswith("FAILED:")
    assert "bad_node" in result


# ---------------------------------------------------------------------------
# formatted_errors()
# ---------------------------------------------------------------------------

def test_formatted_errors_indentation():
    tc = _FailingTest()
    tc._errors = ["node_a", "node_b"]
    result = tc.formatted_errors()
    assert "    node_a\n" in result
    assert "    node_b\n" in result


def test_formatted_errors_empty():
    tc = _PassingTest()
    assert tc.formatted_errors() == ""


# ---------------------------------------------------------------------------
# has_passed()
# ---------------------------------------------------------------------------

def test_has_passed_false_before_run():
    tc = _PassingTest()
    assert tc.has_passed() is False


def test_has_passed_true_after_passing_run():
    tc = _PassingTest()
    tc.run_test()
    assert tc.has_passed() is True


def test_has_passed_false_after_failing_run():
    tc = _FailingTest()
    tc.run_test()
    assert tc.has_passed() is False


# ---------------------------------------------------------------------------
# Class attribute accessors
# ---------------------------------------------------------------------------

def test_name_returns_class_attribute():
    tc = _PassingTest()
    assert tc.name() == "Passing Test"


def test_description_returns_class_attribute():
    tc = _PassingTest()
    assert tc.description() == "Always passes"


def test_category_returns_class_attribute():
    tc = _PassingTest()
    assert tc.category() == "Test"


def test_is_warn_on_failure_default_false():
    tc = _PassingTest()
    assert tc.is_warn_on_failure() is False


def test_select_errors_disabled_by_default():
    tc = _PassingTest()
    assert tc.is_select_errors_enabled() is False


def test_fix_disabled_by_default():
    tc = _PassingTest()
    assert tc.is_fix_errors_enabled() is False


def test_can_retry_on_fix_false_by_default():
    tc = _PassingTest()
    assert tc.can_retry_on_fix() is False
