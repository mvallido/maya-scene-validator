import maya.cmds as cmds
import maya.api.OpenMaya as om

from cz_validation.test_cases.test_case import TestCase


class NgonTest(TestCase):

    NAME = "Ngons"
    DESCRIPTION = "Check for meshes with faces containing more than 4 edges"
    CATEGORY = "Topology"

    PASSED_TEXT = "No ngons found"
    FAILED_TEXT = "Ngons found"

    SELECT_ERRORS_ENABLED = True

    def __init__(self):
        super().__init__()

    def execute(self):
        meshes = cmds.ls(type="mesh", long=True)
        if meshes:
            cmds.select(meshes, replace=True)
            cmds.polySelectConstraint(mode=3,  # All and next
                                      type=8,  # Only select faces
                                      size=3)  # Ngons

            self._errors = cmds.ls(sl=True)

            # Turn off constraint
            cmds.polySelectConstraint(mode=0)
            cmds.select(clear=True)

        return not self._errors


if __name__ == "__main__":
    tc = NgonTest()
    success = tc.run_test()

    print(tc.formatted_results())
    if not success:
        if tc.is_select_errors_enabled():
            tc.select_error_objs()

        if tc.is_fix_errors_enabled():
            tc.fix_errors()
