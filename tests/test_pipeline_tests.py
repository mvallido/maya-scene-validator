"""Unit tests for pipeline test cases: naming convention, unfrozen transforms, missing textures."""
import sys
import pytest
from unittest.mock import patch

from cz_validation.test_cases.model.naming_convention_test import NamingConventionTest
from cz_validation.test_cases.model.unfrozen_transforms_test import UnfrozenTransformsTest
from cz_validation.test_cases.model.missing_textures_test import MissingTexturesTest


@pytest.fixture(autouse=True)
def reset_mocks():
    cmds_mock = sys.modules['maya.cmds']
    om_mock = sys.modules['maya.api.OpenMaya']
    cmds_mock.reset_mock(side_effect=True, return_value=True)
    om_mock.reset_mock(side_effect=True, return_value=True)
    yield
    cmds_mock.reset_mock(side_effect=True, return_value=True)
    om_mock.reset_mock(side_effect=True, return_value=True)


# ---------------------------------------------------------------------------
# NamingConventionTest
# ---------------------------------------------------------------------------

class TestNamingConventionTest:

    def test_pass_no_meshes(self):
        sys.modules['maya.cmds'].ls.return_value = []
        tc = NamingConventionTest()
        assert tc.run_test() is True
        assert tc._errors == []

    def test_pass_correctly_named(self):
        sys.modules['maya.cmds'].ls.return_value = ["pSphereShape1"]
        sys.modules['maya.cmds'].listRelatives.return_value = ["pSphere_geo"]
        tc = NamingConventionTest()
        assert tc.run_test() is True
        assert tc._errors == []

    def test_fail_wrong_suffix(self):
        sys.modules['maya.cmds'].ls.return_value = ["pSphereShape1"]
        sys.modules['maya.cmds'].listRelatives.return_value = ["pSphere1"]
        tc = NamingConventionTest()
        assert tc.run_test() is False
        assert "pSphere1" in tc._errors

    def test_fail_multiple_bad_names(self):
        sys.modules['maya.cmds'].ls.return_value = ["shapeA", "shapeB"]
        sys.modules['maya.cmds'].listRelatives.side_effect = [["badA"], ["badB"]]
        tc = NamingConventionTest()
        assert tc.run_test() is False
        assert set(tc._errors) == {"badA", "badB"}

    def test_custom_suffix(self):
        class _StudioTest(NamingConventionTest):
            GEO_SUFFIX = "_mesh"
        sys.modules['maya.cmds'].ls.return_value = ["boxShape"]
        sys.modules['maya.cmds'].listRelatives.return_value = ["box_mesh"]
        tc = _StudioTest()
        assert tc.run_test() is True

    def test_flags(self):
        tc = NamingConventionTest()
        assert tc.is_select_errors_enabled() is True
        assert tc.is_fix_errors_enabled() is False
        assert tc.category() == "Scene"


# ---------------------------------------------------------------------------
# UnfrozenTransformsTest
# ---------------------------------------------------------------------------

class TestUnfrozenTransformsTest:

    def _frozen_attrs(self, attr):
        if "translate" in attr:
            return [(0.0, 0.0, 0.0)]
        if "rotate" in attr:
            return [(0.0, 0.0, 0.0)]
        if "scale" in attr:
            return [(1.0, 1.0, 1.0)]

    def test_pass_no_meshes(self):
        sys.modules['maya.cmds'].ls.return_value = []
        tc = UnfrozenTransformsTest()
        assert tc.run_test() is True
        assert tc._errors == []

    def test_pass_all_frozen(self):
        sys.modules['maya.cmds'].ls.return_value = ["meshShape"]
        sys.modules['maya.cmds'].listRelatives.return_value = ["mesh_geo"]
        sys.modules['maya.cmds'].getAttr.side_effect = self._frozen_attrs
        tc = UnfrozenTransformsTest()
        assert tc.run_test() is True
        assert tc._errors == []

    def test_fail_non_zero_translate(self):
        sys.modules['maya.cmds'].ls.return_value = ["meshShape"]
        sys.modules['maya.cmds'].listRelatives.return_value = ["mesh_geo"]

        def _attrs(attr):
            if "translate" in attr: return [(1.0, 0.0, 0.0)]
            if "rotate"    in attr: return [(0.0, 0.0, 0.0)]
            if "scale"     in attr: return [(1.0, 1.0, 1.0)]
        sys.modules['maya.cmds'].getAttr.side_effect = _attrs

        tc = UnfrozenTransformsTest()
        assert tc.run_test() is False
        assert "mesh_geo" in tc._errors

    def test_fail_non_unit_scale(self):
        sys.modules['maya.cmds'].ls.return_value = ["meshShape"]
        sys.modules['maya.cmds'].listRelatives.return_value = ["mesh_geo"]

        def _attrs(attr):
            if "translate" in attr: return [(0.0, 0.0, 0.0)]
            if "rotate"    in attr: return [(0.0, 0.0, 0.0)]
            if "scale"     in attr: return [(2.0, 1.0, 1.0)]
        sys.modules['maya.cmds'].getAttr.side_effect = _attrs

        tc = UnfrozenTransformsTest()
        assert tc.run_test() is False
        assert "mesh_geo" in tc._errors

    def test_deduplicates_shared_transform(self):
        """Two shapes under the same transform should only produce one error."""
        sys.modules['maya.cmds'].ls.return_value = ["shapeA", "shapeB"]
        sys.modules['maya.cmds'].listRelatives.return_value = ["shared_transform"]

        def _attrs(attr):
            if "translate" in attr: return [(5.0, 0.0, 0.0)]
            if "rotate"    in attr: return [(0.0, 0.0, 0.0)]
            if "scale"     in attr: return [(1.0, 1.0, 1.0)]
        sys.modules['maya.cmds'].getAttr.side_effect = _attrs

        tc = UnfrozenTransformsTest()
        tc.run_test()
        assert tc._errors.count("shared_transform") == 1

    def test_fix_calls_make_identity(self):
        tc = UnfrozenTransformsTest()
        tc._errors = ["mesh_geo"]
        tc.fix_errors()
        sys.modules['maya.cmds'].makeIdentity.assert_called_once_with(
            "mesh_geo", apply=True, translate=True, rotate=True, scale=True
        )
        sys.modules['maya.api.OpenMaya'].MGlobal.displayInfo.assert_called_once()

    def test_flags(self):
        tc = UnfrozenTransformsTest()
        assert tc.is_select_errors_enabled() is True
        assert tc.is_fix_errors_enabled() is True
        assert tc.can_retry_on_fix() is True
        assert tc.category() == "Transforms"


# ---------------------------------------------------------------------------
# MissingTexturesTest
# ---------------------------------------------------------------------------

_MODULE = 'cz_validation.test_cases.model.missing_textures_test.os.path.exists'


class TestMissingTexturesTest:

    def test_pass_no_file_nodes(self):
        sys.modules['maya.cmds'].ls.return_value = []
        tc = MissingTexturesTest()
        assert tc.run_test() is True
        assert tc._errors == []

    def test_pass_all_textures_exist(self):
        sys.modules['maya.cmds'].ls.return_value = ["file1"]
        sys.modules['maya.cmds'].getAttr.return_value = "/textures/diffuse.png"
        with patch(_MODULE, return_value=True):
            tc = MissingTexturesTest()
            assert tc.run_test() is True
            assert tc._errors == []

    def test_fail_missing_file(self):
        sys.modules['maya.cmds'].ls.return_value = ["file1"]
        sys.modules['maya.cmds'].getAttr.return_value = "/textures/missing.png"
        with patch(_MODULE, return_value=False):
            tc = MissingTexturesTest()
            assert tc.run_test() is False
            assert any("file1" in e for e in tc._errors)

    def test_fail_empty_path(self):
        sys.modules['maya.cmds'].ls.return_value = ["file1"]
        sys.modules['maya.cmds'].getAttr.return_value = ""
        tc = MissingTexturesTest()
        assert tc.run_test() is False
        assert any("no path set" in e for e in tc._errors)

    def test_flags(self):
        tc = MissingTexturesTest()
        assert tc.is_select_errors_enabled() is False
        assert tc.is_fix_errors_enabled() is False
        assert tc.category() == "Textures"
