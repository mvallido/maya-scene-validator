from .model.empty_mesh_test import EmptyMeshTest
from .model.duplicate_names_test import DuplicateNamesTest
from .model.triangular_faces_test import TriangularFacesTest
from .model.n_sided_faces_test import NSidedFacesTest


def all_test_cases():
    return [
        EmptyMeshTest(),
        DuplicateNamesTest(),
        TriangularFacesTest(),
        NSidedFacesTest(),
    ]
