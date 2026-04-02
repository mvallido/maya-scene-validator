import maya.cmds as cmds
import maya.api.OpenMaya as om

from cz_validation.test_cases.test_case import TestCase


class UnfrozenTransformsTest(TestCase):

    NAME = "Unfrozen Transforms"
    DESCRIPTION = "Check that all mesh transforms have frozen translate, rotate, and scale"
    CATEGORY = "Transforms"

    PASSED_TEXT = "All transforms are frozen"
    FAILED_TEXT = "Unfrozen transforms found"

    SELECT_ERRORS_ENABLED = True
    FIX_ENABLED = True
    CAN_RETRY_ON_FIX = True

    def __init__(self):
        super().__init__()

    def execute(self):
        meshes = cmds.ls(type="mesh")
        seen = set()
        for mesh in meshes:
            parents = cmds.listRelatives(mesh, parent=True) or []
            for transform in parents:
                if transform in seen:
                    continue
                seen.add(transform)
                t = cmds.getAttr(transform + ".translate")[0]
                r = cmds.getAttr(transform + ".rotate")[0]
                s = cmds.getAttr(transform + ".scale")[0]
                if (any(abs(v) > 1e-4 for v in t) or
                        any(abs(v) > 1e-4 for v in r) or
                        any(abs(v - 1.0) > 1e-4 for v in s)):
                    self._errors.append(transform)
        return not self._errors

    def fix_errors(self):
        for transform in self._errors:
            try:
                cmds.makeIdentity(transform, apply=True,
                                  translate=True, rotate=True, scale=True)
            except Exception:
                om.MGlobal.displayWarning(f"Failed to freeze: {transform}")
        om.MGlobal.displayInfo("Transforms frozen")


if __name__ == "__main__":
    tc = UnfrozenTransformsTest()
    success = tc.run_test()

    print(tc.formatted_results())
    if not success:
        if tc.is_select_errors_enabled():
            tc.select_error_objs()

        if tc.is_fix_errors_enabled():
            tc.fix_errors()
