import maya.cmds as cmds
import maya.api.OpenMaya as om

from cz_validation.test_cases.test_case import TestCase


class EmptyMeshTest(TestCase):

    NAME = "Empty meshes"
    DESCRIPTION = "Check for meshes with zero vertices"
    CATEGORY = "Meshes"

    PASSED_TEXT = "No empty meshes"
    FAILED_TEXT = "Empty meshes found"

    SELECT_ERRORS_ENABLED = True
    FIX_ENABLED = True
    CAN_RETRY_ON_FIX = True

    def __init__(self):
        super().__init__()

    def execute(self):
        meshes = cmds.ls(type="mesh")
        for mesh in meshes:
            vertex_count = cmds.polyEvaluate(mesh, vertex=True)
            if vertex_count == 0:
                self._errors.append(mesh)
        return not self._errors

    def fix_errors(self):
        exception_count = 0
        for mesh in self._errors:
            try:
                parent = cmds.listRelatives(mesh, parent=True, fullPath=True)[0]
                cmds.delete(parent)
            except:
                om.MGlobal.displayWarning(f"Failed to delete empty mesh: {mesh}")
                exception_count += 1

        if exception_count == 0:
            om.MGlobal.displayInfo("All empty meshes have been deleted")


if __name__ == "__main__":
    tc = EmptyMeshTest()
    success = tc.run_test()

    print(tc.formatted_results())
    if not success:
        if tc.is_select_errors_enabled():
            tc.select_error_objs()

        if tc.is_fix_errors_enabled():
            tc.fix_errors()
