import maya.cmds as cmds
import maya.api.OpenMaya as om

from cz_validation.test_cases.test_case import TestCase


class TriangularFacesTest(TestCase):

    NAME = "Triangular Faces"
    DESCRIPTION = "Check for meshes with triangular faces"
    CATEGORY = "Topology"

    PASSED_TEXT = "No triangular faces"
    FAILED_TEXT = "Triangular faces found"

    WARN_ON_FAILURE = True

    SELECT_ERRORS_ENABLED = True

    def __init__(self):
        super().__init__()

    def execute(self):
        meshes = cmds.ls(type="mesh", long=True)
        if meshes:
            cmds.select(meshes, replace=True)
            cmds.polySelectConstraint(mode=3,  # All and next
                                      type=8,  # Only select faces
                                      size=1)  # Triangles

            self._errors = cmds.ls(sl=True)

            # Turn off constraint
            cmds.polySelectConstraint(mode=0)
            cmds.select(clear=True)

        return not self._errors


if __name__ == "__main__":
    tc = TriangularFacesTest()
    success = tc.run_test()

    print(tc.formatted_results())
    if not success:
        if tc.is_select_errors_enabled():
            tc.select_error_objs()

        if tc.is_fix_errors_enabled():
            tc.fix_errors()
