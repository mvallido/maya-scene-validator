import maya.cmds as cmds
import maya.api.OpenMaya as om

from cz_validation.test_cases.test_case import TestCase


class NamingConventionTest(TestCase):

    NAME = "Naming Conventions"
    DESCRIPTION = "Check that mesh transforms follow the naming convention (default: _geo suffix)"
    CATEGORY = "Scene"

    PASSED_TEXT = "All mesh transforms are correctly named"
    FAILED_TEXT = "Incorrectly named mesh transforms found"

    GEO_SUFFIX = "_geo"

    SELECT_ERRORS_ENABLED = True

    def __init__(self):
        super().__init__()

    def execute(self):
        meshes = cmds.ls(type="mesh")
        for mesh in meshes:
            parents = cmds.listRelatives(mesh, parent=True) or []
            for parent in parents:
                if not parent.endswith(self.__class__.GEO_SUFFIX):
                    self._errors.append(parent)
        return not self._errors


if __name__ == "__main__":
    tc = NamingConventionTest()
    success = tc.run_test()

    print(tc.formatted_results())
    if not success:
        if tc.is_select_errors_enabled():
            tc.select_error_objs()
