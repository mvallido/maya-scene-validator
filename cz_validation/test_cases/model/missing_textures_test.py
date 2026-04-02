import os

import maya.cmds as cmds
import maya.api.OpenMaya as om

from cz_validation.test_cases.test_case import TestCase


class MissingTexturesTest(TestCase):

    NAME = "Missing Textures"
    DESCRIPTION = "Check that all file texture nodes reference paths that exist on disk"
    CATEGORY = "Textures"

    PASSED_TEXT = "All texture paths are valid"
    FAILED_TEXT = "Missing or unset texture paths found"

    def __init__(self):
        super().__init__()

    def execute(self):
        file_nodes = cmds.ls(type="file")
        for node in file_nodes:
            path = cmds.getAttr(node + ".fileTextureName")
            if not path or not os.path.exists(path):
                self._errors.append(f"{node}: {path or 'no path set'}")
        return not self._errors


if __name__ == "__main__":
    tc = MissingTexturesTest()
    success = tc.run_test()

    print(tc.formatted_results())
