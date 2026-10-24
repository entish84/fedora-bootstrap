"""Sandboxed isolated test of dotfiles backup and symlink topology."""

from pathlib import Path
import sys
import tempfile
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.context import ExecutionContext
from modules.dotfiles import DotfilesTask


class TestDotfilesSandbox(unittest.TestCase):
    def test_fallback_dotfiles_deployment_and_backup(self):
        with tempfile.TemporaryDirectory() as tmp_home:
            fake_home = Path(tmp_home)

            ctx = ExecutionContext.detect(dry_run=False)
            ctx.target_home = fake_home
            ctx.use_fallback_dotfiles = True
            ctx.dotfiles_repo = None

            # Simulate existing old configuration files
            old_zshrc = fake_home / ".zshrc"
            old_zshrc.write_text("# Old custom zshrc", encoding="utf-8")

            old_kitty = fake_home / ".config" / "kitty" / "kitty.conf"
            old_kitty.parent.mkdir(parents=True, exist_ok=True)
            old_kitty.write_text("# Old kitty", encoding="utf-8")

            # Execute DotfilesTask in the sandboxed fake_home
            task = DotfilesTask()
            result = task.apply(ctx)
            self.assertTrue(result)

            # 1. Verify ~/.dotfiles directory populated
            dotfiles_dir = fake_home / ".dotfiles"
            self.assertTrue(dotfiles_dir.exists())
            self.assertTrue((dotfiles_dir / ".zshrc").exists())
            self.assertTrue((dotfiles_dir / ".zsh_aliases").exists())
            self.assertTrue((dotfiles_dir / ".config" / "kitty" / "kitty.conf").exists())
            self.assertTrue((dotfiles_dir / ".config" / "kitty" / "current-theme.conf").exists())
            self.assertTrue((dotfiles_dir / ".config" / "starship.toml").exists())

            # 2. Verify non-destructive backup was created
            backup_dirs = list(fake_home.glob(".dotfiles_backup_*"))
            self.assertEqual(len(backup_dirs), 1, "Expected one backup directory to be created")
            backup_zshrc = backup_dirs[0] / ".zshrc"
            self.assertTrue(backup_zshrc.exists())
            self.assertEqual(backup_zshrc.read_text(), "# Old custom zshrc")

            # 3. Verify destination files are now proper symlinks
            new_zshrc = fake_home / ".zshrc"
            self.assertTrue(new_zshrc.is_symlink())
            self.assertEqual(new_zshrc.resolve(), (dotfiles_dir / ".zshrc").resolve())

            new_kitty = fake_home / ".config" / "kitty" / "kitty.conf"
            self.assertTrue(new_kitty.is_symlink())
            self.assertEqual(new_kitty.resolve(), (dotfiles_dir / ".config" / "kitty" / "kitty.conf").resolve())

            # 4. Verify idempotency check
            self.assertTrue(task.check(ctx))


if __name__ == "__main__":
    unittest.main()
