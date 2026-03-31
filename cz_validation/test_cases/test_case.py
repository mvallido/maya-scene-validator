import maya.cmds as cmds
import maya.api.OpenMaya as om


class TestCase(object):

    NAME = "<Test Case>"
    DESCRIPTION = "<Test Case Description>"

    PASSED_TEXT = "<Test Case Passed Text>"
    FAILED_TEXT = "<Test Case Failed Test>"

    WARN_ON_FAILURE = False

    SELECT_ERRORS_ENABLED = False
    FIX_ENABLED = False
    CAN_RETRY_ON_FIX = False

    def __init__(self):
        self.reset()

    def reset(self):
        self._run_completed = False
        self._passed = False

        self._errors = []

    def run_test(self):
        self.reset()
        self._passed = self.execute()
        self._run_completed = True

        return self._passed

    def execute(self):
        # Override this method in derived class
        self._errors.append("execute() method not implemented")
        om.MGlobal.displayError(f"{self.name()} execute() method not implemented")
        return False

    def select_error_objs(self):
        if self.SELECT_ERRORS_ENABLED:
            cmds.select(clear=True)

            if self._errors:
                cmds.select(self._errors, replace=True)

    def fix_errors(self):
        om.MGlobal.displayError("fix_error() method not implemented")

    def formatted_results(self):
        result_str = ""

        if not self._run_completed:
            result_str += f"NOT RUN: {self.name()}"
        else:
            if self._passed:
                result_str += f"PASSED: {self.passed_text()}"
            else:
                result_str += f"FAILED: {self.failed_text()}\n"
                result_str += self.formatted_errors()

        return result_str

    def formatted_errors(self):
        error_str = ""
        for err in self._errors:
            error_str += f"    {err}\n"

        return error_str

    def name(self):
        return self.__class__.NAME

    def description(self):
        return self.__class__.DESCRIPTION

    def passed_text(self):
        return self.__class__.DESCRIPTION

    def failed_text(self):
        error_count = len(self._errors)
        return f"{self.__class__.FAILED_TEXT} ({error_count})"

    def is_warn_on_failure(self):
        return self.__class__.WARN_ON_FAILURE

    def is_select_errors_enabled(self):
        return self.__class__.SELECT_ERRORS_ENABLED

    def is_fix_errors_enabled(self):
        return self.__class__.FIX_ENABLED

    def can_retry_on_fix(self):
        return self.__class__.CAN_RETRY_ON_FIX

    def has_run_completed(self):
        return self._run_completed

    def has_passed(self):
        if self._run_completed:
            return self._passed
        return False


tc = TestCase()
s = tc.run_test()
if not s and tc.is_select_errors_enabled():
    tc.select_error_objs()

print(tc.formatted_results())
