from .model.empty_mesh_test import EmptyMeshTest
from .model.duplicate_names_test import DuplicateNamesTest
from .model.naming_convention_test import NamingConventionTest
from .model.triangular_faces_test import TriangularFacesTest
from .model.ngon_test import NgonTest
from .model.unfrozen_transforms_test import UnfrozenTransformsTest
from .model.missing_textures_test import MissingTexturesTest


def all_test_cases():
    return [
        EmptyMeshTest(),
        DuplicateNamesTest(),
        NamingConventionTest(),
        TriangularFacesTest(),
        NgonTest(),
        UnfrozenTransformsTest(),
        MissingTexturesTest(),
    ]
