"""Check that all permission strings used in the code are defined in General."""

# Standard Library
import re
from pathlib import Path

# Django
from django.test import SimpleTestCase

# AA Memberaudit Doctrine Checker
import madc
from madc.models.general import General

# Matches e.g. "madc.basic_access" and "perms.madc.basic_access", also typos
PERMISSION_PATTERN = re.compile(r"\bmadc\.(\w*access\w*)", re.IGNORECASE)


class TestPermissionStrings(SimpleTestCase):
    def test_used_permissions_exist_in_general(self):
        """Every permission string in the code must match a codename of General."""
        defined = {codename for codename, _ in General._meta.permissions}
        root = Path(madc.__file__).parent
        used = {}
        for path in root.rglob("*"):
            if path.suffix not in {".py", ".html"} or "tests" in path.parts:
                continue
            if "migrations" in path.parts:
                continue
            text = path.read_text(encoding="utf-8")
            for match in PERMISSION_PATTERN.finditer(text):
                used.setdefault(match.group(1), set()).add(path.name)

        self.assertTrue(used, "No permission strings found, pattern is broken.")
        unknown = {k: sorted(v) for k, v in used.items() if k not in defined}
        self.assertEqual(unknown, {})

    def test_all_defined_permissions_are_used(self):
        """Every permission defined in General must be checked somewhere."""
        defined = {codename for codename, _ in General._meta.permissions}
        root = Path(madc.__file__).parent
        used = set()
        for path in root.rglob("*"):
            if path.suffix not in {".py", ".html"} or "tests" in path.parts:
                continue
            if "migrations" in path.parts:
                continue
            used |= set(PERMISSION_PATTERN.findall(path.read_text(encoding="utf-8")))
        self.assertEqual(defined - used, set())
