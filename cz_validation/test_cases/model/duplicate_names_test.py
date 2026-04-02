import maya.cmds as cmds
import maya.api.OpenMaya as om

from cz_validation.test_cases.test_case import TestCase

from RenameTool_UI import renameTool


class DuplicateNamesTest(TestCase):

    NAME = "Duplicate Names"
    DESCRIPTION = "Check for duplicate node names"
    CATEGORY = "Scene"

    PASSED_TEXT = "No duplicate node names"
    FAILED_TEXT = "Duplicate node names found"

    SELECT_ERRORS_ENABLED = True
    FIX_ENABLED = True

    def __init__(self):
        super().__init__()

    def execute(self):
        transform_nodes = cmds.ls(transforms=True)
        for node in transform_nodes:
            if '|' in node:
                self._errors.append(node)

        return not self._errors

    def select_error_objs(self):
        super().select_error_objs()

    def fix_errors(self):
        renameTool.show_dialog()


if __name__ == "__main__":
    tc = DuplicateNamesTest()
    success = tc.run_test()

    print(tc.formatted_results())
    if not success:
        if tc.is_select_errors_enabled():
            tc.select_error_objs()

        if tc.is_fix_errors_enabled():
            tc.fix_errors()
