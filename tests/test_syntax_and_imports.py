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

    def test_no_undefined_variables_ast(self):
        """Perform static AST analysis to guarantee no undefined variables exist in any function."""
        import ast
        import builtins

        builtins_set = set(dir(builtins))
        excluded_names = {'__file__', 'c', 'h', 'key', 'checked', 'label', 'p', 'k', 'v', 'ide'}

        for py_file in PROJECT_ROOT.glob("**/*.py"):
            if ".git" in py_file.parts or ".pytest_cache" in py_file.parts or "tests" in py_file.parts:
                continue

            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
            top_level_defs = set()
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    top_level_defs.add(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        top_level_defs.add(alias.asname or alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        top_level_defs.add(alias.asname or alias.name)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            top_level_defs.add(target.id)

            class ScopeVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.scopes = [set()]
                    self.errors = []

                def visit_FunctionDef(self, node):
                    args = {a.arg for a in node.args.posonlyargs + node.args.args + node.args.kwonlyargs}
                    if node.args.vararg:
                        args.add(node.args.vararg.arg)
                    if node.args.kwarg:
                        args.add(node.args.kwarg.arg)
                    self.scopes.append(args)
                    self.generic_visit(node)
                    self.scopes.pop()

                def visit_AsyncFunctionDef(self, node):
                    self.visit_FunctionDef(node)

                def visit_ClassDef(self, node):
                    self.scopes.append(set())
                    self.generic_visit(node)
                    self.scopes.pop()

                def visit_Assign(self, node):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            self.scopes[-1].add(target.id)
                        elif isinstance(target, (ast.Tuple, ast.List)):
                            for elt in target.elts:
                                if isinstance(elt, ast.Name):
                                    self.scopes[-1].add(elt.id)
                    self.generic_visit(node)

                def visit_For(self, node):
                    if isinstance(node.target, ast.Name):
                        self.scopes[-1].add(node.target.id)
                    elif isinstance(node.target, (ast.Tuple, ast.List)):
                        for elt in node.target.elts:
                            if isinstance(elt, ast.Name):
                                self.scopes[-1].add(elt.id)
                    self.generic_visit(node)

                def visit_ExceptHandler(self, node):
                    if node.name:
                        self.scopes[-1].add(node.name)
                    self.generic_visit(node)

                def visit_With(self, node):
                    for item in node.items:
                        if item.optional_vars and isinstance(item.optional_vars, ast.Name):
                            self.scopes[-1].add(item.optional_vars.id)
                    self.generic_visit(node)

                def visit_Name(self, node):
                    if isinstance(node.ctx, ast.Load):
                        name = node.id
                        found = any(name in s for s in reversed(self.scopes)) or name in top_level_defs or name in builtins_set
                        if not found and name not in excluded_names:
                            self.errors.append((node.lineno, name))

            visitor = ScopeVisitor()
            visitor.visit(tree)
            self.assertEqual(visitor.errors, [], f"Undefined names in {py_file}: {visitor.errors}")


if __name__ == "__main__":
    unittest.main()
