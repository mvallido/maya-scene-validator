"""
Inject maya module mocks into sys.modules before any cz_validation import.
This must run before test collection — conftest.py at the root of tests/ guarantees that.

Root cause note: `import maya.cmds as cmds` compiles to IMPORT_FROM which calls
getattr(sys.modules['maya'], 'cmds'), NOT sys.modules['maya.cmds'].  We must set
the attribute on the parent mock so both resolve to the same object.
"""
import sys
from unittest.mock import MagicMock

_maya = MagicMock()
_maya_cmds = MagicMock()
_maya_api = MagicMock()
_maya_api_om = MagicMock()

# Wire attributes on parent mocks BEFORE setting sys.modules so that
# `import maya.cmds as cmds` and `import maya.api.OpenMaya as om` resolve
# to the same objects that tests configure.
_maya.cmds = _maya_cmds
_maya.api = _maya_api
_maya_api.OpenMaya = _maya_api_om

sys.modules['maya'] = _maya
sys.modules['maya.cmds'] = _maya_cmds
sys.modules['maya.api'] = _maya_api
sys.modules['maya.api.OpenMaya'] = _maya_api_om

# DuplicateNamesTest imports RenameTool_UI at module level
sys.modules['RenameTool_UI'] = MagicMock()
sys.modules['RenameTool_UI.renameTool'] = MagicMock()
