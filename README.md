# Asset Validator

![Asset Validator UI](docs/screenshot.png)

A Maya 2026 tool for automated asset validation built with PySide6. It runs a configurable suite of checks against the active scene — topology, naming conventions, transforms, and textures — and presents results in a dockable dark-themed UI. Each check reports pass/fail with selectable error nodes and, where applicable, a one-click fix. Designed as a foundation for a studio pipeline validator that a TD can extend by subclassing `TestCase`.

## Requirements

- Autodesk Maya 2026 (PySide6 / Python 3.11)
- No third-party dependencies

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/<your-username>/asset-validator.git
   ```

2. Add the repo root to Maya's Python path. In `userSetup.py` (found in your Maya scripts directory):
   ```python
   import sys
   sys.path.insert(0, "/path/to/asset-validator")
   ```

3. Restart Maya.

## Running

In the Maya Script Editor (Python tab):
```python
import cz_validation
cz_validation.show()
```

Or paste the following into a shelf button for one-click access:
```python
import importlib, cz_validation, cz_validation.ui.validator_window
importlib.reload(cz_validation.ui.validator_window)
import cz_validation
cz_validation.show()
```

## Checks

| Category   | Check                 | Select | Fix |
|------------|-----------------------|--------|-----|
| Meshes     | Empty Meshes          | ✓      | ✓   |
| Scene      | Duplicate Names       | ✓      | ✓   |
| Scene      | Naming Conventions    | ✓      |     |
| Topology   | Triangular Faces      | ✓      |     |
| Topology   | Ngons                 | ✓      |     |
| Transforms | Unfrozen Transforms   | ✓      | ✓   |
| Textures   | Missing Textures      |        |     |

**Empty Meshes** — flags mesh nodes with zero vertices and deletes their parent transforms on fix.

**Duplicate Names** — flags any node whose full path contains `|`, indicating a non-unique name. Opens a rename utility on fix.

**Naming Conventions** — flags mesh transforms that do not end with the configured suffix (default `_geo`). The suffix is overridable per-studio by subclassing.

**Triangular Faces** — warns on meshes containing tri faces (warning only, does not block export).

**Ngons** — flags faces with more than 4 edges.

**Unfrozen Transforms** — flags mesh transforms with non-identity translate, rotate, or scale. Freezes transforms on fix.

**Missing Textures** — flags file texture nodes whose path does not exist on disk or has no path set.

## Running Tests

The test suite mocks all Maya dependencies and runs without a Maya installation:

```
python -m pytest tests/ -v
```

64 tests across `test_case.py` base class, model checks, and pipeline checks.

## Adding a Check

Subclass `TestCase` and implement `execute()`:

```python
from cz_validation.test_cases.test_case import TestCase

class MyCheck(TestCase):
    NAME        = "My Check"
    DESCRIPTION = "What this checks"
    CATEGORY    = "Scene"

    SELECT_ERRORS_ENABLED = True

    def execute(self):
        # populate self._errors, return True if clean
        return not self._errors
```

Register it in `cz_validation/test_cases/__init__.py` and it will appear in the UI automatically.
