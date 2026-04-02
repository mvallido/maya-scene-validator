"""Unit tests for model test case execute() and fix_errors() logic."""
import sys
import pytest

# conftest.py has injected maya mocks — safe to import
from cz_validation.test_cases.model.empty_mesh_test import EmptyMeshTest
from cz_validation.test_cases.model.duplicate_names_test import DuplicateNamesTest
from cz_validation.test_cases.model.triangular_faces_test import TriangularFacesTest
from cz_validation.test_cases.model.ngon_test import NgonTest


@pytest.fixture(autouse=True)
def reset_mocks():
    """Fully reset maya mocks between tests — clears side_effects and return_values."""
    cmds_mock = sys.modules['maya.cmds']
    om_mock = sys.modules['maya.api.OpenMaya']
    cmds_mock.reset_mock(side_effect=True, return_value=True)
    om_mock.reset_mock(side_effect=True, return_value=True)
    yield
    cmds_mock.reset_mock(side_effect=True, return_value=True)
    om_mock.reset_mock(side_effect=True, return_value=True)


# ---------------------------------------------------------------------------
# EmptyMeshTest
# ---------------------------------------------------------------------------

class TestEmptyMeshTest:

    def test_pass_no_meshes(self):
        sys.modules['maya.cmds'].ls.return_value = []
        tc = EmptyMeshTest()
        assert tc.run_test() is True
        assert tc._errors == []

    def test_pass_all_have_vertices(self):
        sys.modules['maya.cmds'].ls.return_value = ["mesh1", "mesh2"]
        sys.modules['maya.cmds'].polyEvaluate.return_value = 100
        tc = EmptyMeshTest()
        assert tc.run_test() is True
        assert tc._errors == []

    def test_fail_one_empty_mesh(self):
        sys.modules['maya.cmds'].ls.return_value = ["mesh1", "empty_mesh"]
        sys.modules['maya.cmds'].polyEvaluate.side_effect = (
            lambda mesh, vertex: 0 if mesh == "empty_mesh" else 100
        )
        tc = EmptyMeshTest()
        assert tc.run_test() is False
        assert tc._errors == ["empty_mesh"]

    def test_fail_multiple_empty_meshes(self):
        sys.modules['maya.cmds'].ls.return_value = ["empty_a", "empty_b", "good_mesh"]
        sys.modules['maya.cmds'].polyEvaluate.side_effect = (
            lambda mesh, vertex: 0 if mesh.startswith("empty") else 50
        )
        tc = EmptyMeshTest()
        assert tc.run_test() is False
        assert set(tc._errors) == {"empty_a", "empty_b"}

    def test_fix_deletes_parent_transform(self):
        sys.modules['maya.cmds'].listRelatives.return_value = ["|root|empty_transform"]
        tc = EmptyMeshTest()
        tc._errors = ["empty_mesh"]
        tc.fix_errors()
        sys.modules['maya.cmds'].delete.assert_called_once_with("|root|empty_transform")
        sys.modules['maya.api.OpenMaya'].MGlobal.displayInfo.assert_called_once()

    def test_fix_handles_exception_gracefully(self):
        sys.modules['maya.cmds'].listRelatives.side_effect = Exception("node not found")
        tc = EmptyMeshTest()
        tc._errors = ["bad_mesh"]
        tc.fix_errors()  # must not raise
        sys.modules['maya.api.OpenMaya'].MGlobal.displayWarning.assert_called_once()

    def test_fix_partial_failure_reports_warning(self):
        sys.modules['maya.cmds'].listRelatives.side_effect = [
            Exception("fail"), ["|root|ok_transform"]
        ]
        tc = EmptyMeshTest()
        tc._errors = ["bad_mesh", "ok_mesh"]
        tc.fix_errors()
        assert sys.modules['maya.api.OpenMaya'].MGlobal.displayWarning.call_count == 1

    def test_flags(self):
        tc = EmptyMeshTest()
        assert tc.is_select_errors_enabled() is True
        assert tc.is_fix_errors_enabled() is True
        assert tc.can_retry_on_fix() is True
        assert tc.category() == "Meshes"


# ---------------------------------------------------------------------------
# DuplicateNamesTest
# ---------------------------------------------------------------------------

class TestDuplicateNamesTest:

    def test_pass_no_duplicates(self):
        sys.modules['maya.cmds'].ls.return_value = ["root", "child", "geo"]
        tc = DuplicateNamesTest()
        assert tc.run_test() is True
        assert tc._errors == []

    def test_fail_node_with_pipe(self):
        sys.modules['maya.cmds'].ls.return_value = ["root", "|root|child", "|root|child2"]
        tc = DuplicateNamesTest()
        assert tc.run_test() is False
        assert "|root|child" in tc._errors
        assert "|root|child2" in tc._errors

    def test_fail_only_pipe_nodes_collected(self):
        sys.modules['maya.cmds'].ls.return_value = ["clean_node", "|dup|node"]
        tc = DuplicateNamesTest()
        tc.run_test()
        assert "clean_node" not in tc._errors

    def test_fix_calls_rename_tool(self):
        tc = DuplicateNamesTest()
        tc.fix_errors()
        sys.modules['RenameTool_UI'].renameTool.show_dialog.assert_called_once()

    def test_flags(self):
        tc = DuplicateNamesTest()
        assert tc.is_select_errors_enabled() is True
        assert tc.is_fix_errors_enabled() is True
        assert tc.category() == "Scene"


# ---------------------------------------------------------------------------
# TriangularFacesTest
# ---------------------------------------------------------------------------

class TestTriangularFacesTest:

    def test_pass_no_meshes(self):
        sys.modules['maya.cmds'].ls.return_value = []
        tc = TriangularFacesTest()
        assert tc.run_test() is True
        assert tc._errors == []
        sys.modules['maya.cmds'].polySelectConstraint.assert_not_called()

    def test_pass_no_triangular_faces(self):
        sys.modules['maya.cmds'].ls.side_effect = [["mesh1"], []]
        tc = TriangularFacesTest()
        assert tc.run_test() is True
        assert tc._errors == []

    def test_fail_has_triangular_faces(self):
        sys.modules['maya.cmds'].ls.side_effect = [["mesh1"], ["mesh1.f[0]", "mesh1.f[5]"]]
        tc = TriangularFacesTest()
        assert tc.run_test() is False
        assert tc._errors == ["mesh1.f[0]", "mesh1.f[5]"]

    def test_polySelectConstraint_turned_off_after_run(self):
        sys.modules['maya.cmds'].ls.side_effect = [["mesh1"], ["mesh1.f[0]"]]
        tc = TriangularFacesTest()
        tc.run_test()
        sys.modules['maya.cmds'].polySelectConstraint.assert_called_with(mode=0)

    def test_warn_on_failure_flag(self):
        assert TriangularFacesTest.WARN_ON_FAILURE is True

    def test_flags(self):
        tc = TriangularFacesTest()
        assert tc.is_select_errors_enabled() is True
        assert tc.is_fix_errors_enabled() is False
        assert tc.category() == "Topology"


# ---------------------------------------------------------------------------
# NgonTest
# ---------------------------------------------------------------------------

class TestNgonTest:

    def test_pass_no_meshes(self):
        sys.modules['maya.cmds'].ls.return_value = []
        tc = NgonTest()
        assert tc.run_test() is True
        assert tc._errors == []

    def test_pass_no_nsided_faces(self):
        sys.modules['maya.cmds'].ls.side_effect = [["mesh1"], []]
        tc = NgonTest()
        assert tc.run_test() is True

    def test_fail_has_nsided_faces(self):
        sys.modules['maya.cmds'].ls.side_effect = [["mesh1"], ["mesh1.f[10]"]]
        tc = NgonTest()
        assert tc.run_test() is False
        assert "mesh1.f[10]" in tc._errors

    def test_polySelectConstraint_size_3_for_nsided(self):
        """N-sided check must use size=3, not size=1 (triangles)."""
        sys.modules['maya.cmds'].ls.side_effect = [["mesh1"], []]
        tc = NgonTest()
        tc.run_test()
        calls = sys.modules['maya.cmds'].polySelectConstraint.call_args_list
        constraint_call = next(c for c in calls if c.kwargs.get('size') is not None)
        assert constraint_call.kwargs['size'] == 3

    def test_flags(self):
        tc = NgonTest()
        assert tc.is_select_errors_enabled() is True
        assert tc.is_fix_errors_enabled() is False
        assert tc.category() == "Topology"
