from .model.empty_mesh_test import EmptyMeshTest
from .model.duplicate_names_test import DuplicateNamesTest
from .model.triangular_faces_test import TriangularFacesTest
from .model.ngon_test import NgonTest


def all_test_cases():
    return [
        EmptyMeshTest(),
        DuplicateNamesTest(),
        TriangularFacesTest(),
        NgonTest(),
    ]
