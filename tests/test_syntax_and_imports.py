"""Verify that all Python files compile cleanly and can be imported without errors."""

import importlib
from pathlib import Path
import py_compile
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestSyntaxAndImports(unittest.TestCase):
    def test_py_compile_all_files(self):
        """Ensure all python files in the project compile with zero syntax errors."""
        py_files = list(PROJECT_ROOT.glob("**/*.py"))
        self.assertGreater(len(py_files), 10, "Expected at least 10 Python files in project")

        for py_file in py_files:
            try:
                py_compile.compile(str(py_file), doraise=True)
            except py_compile.PyCompileError as e:
                self.fail(f"Syntax error in {py_file}: {e}")

    def test_module_imports(self):
        """Ensure core and modules can be imported cleanly."""
        modules_to_test = [
            "core.context",
            "core.logger",
            "core.executor",
            "core.state",
            "core.ui",
            "modules.base",
            "modules.dnf_config",
            "modules.repositories",
            "modules.multimedia",
            "modules.nvidia",
            "modules.packages",
            "modules.dev_tools",
            "modules.desktop_gnome",
            "modules.desktop_dms_niri",
            "modules.wallpapers",
            "modules.virtualization",
            "modules.shell_env",
            "modules.neovim_dotnet",
            "modules.ides",
            "modules.dotfiles",
            "modules.git_onboard",
            "modules.system_tuning",
            "modules.security",
        ]

        for mod in modules_to_test:
            try:
                importlib.import_module(mod)
            except Exception as e:
                self.fail(f"Failed to import {mod}: {e}")


if __name__ == "__main__":
    unittest.main()
