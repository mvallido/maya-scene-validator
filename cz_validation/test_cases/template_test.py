import maya.cmds as cmds
import maya.api.OpenMaya as om

from cz_validation.test_cases.test_case import TestCase

class TemplateTest(TestCase):

    NAME = "<Template Test>"
    DESCRIPTION = "<Template Test Description>"

    PASSED_TEXT = "<Template Test Passed Text>"
    FAILED_TEXT = "<Template Test Failed Test>"

    WARN_ON_FAILURE = False

    SELECT_ERRORS_ENABLED = False
    FIX_ENABLED = False
    CAN_RETRY_ON_FIX = False

    def __init__(self):
        super().__init__()

    def execute(self):
        return super().execute()

    def select_error_objs(self):
        super().select_error_objs()

    def fix_errors(self):
        super().fix_errors()

    def formatted_errors(self):
        return super().formatted_errors()


if __name__ == "__main__":
    tc = TestCase()

    success = tc.run_test()
    if not success and tc.is_select_errors_enabled():
        tc.select_error_objs()

    print(tc.formatted_results())
