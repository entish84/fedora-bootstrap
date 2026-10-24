"""Dry-run pipeline simulation test across Workstation and Minimal profiles."""

from pathlib import Path
import sys
import tempfile
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.context import ExecutionContext
from core.state import StateTracker
from modules.base import TaskRunner
from modules.dnf_config import DnfConfigTask
from modules.repositories import RepositoriesTask
from modules.multimedia import MultimediaTask
from modules.nvidia import NvidiaTask
from modules.packages import PackagesTask
from modules.dev_tools import DevToolsTask
from modules.desktop_gnome import DesktopGnomeTask
from modules.desktop_dms_niri import DesktopDmsNiriTask
from modules.wallpapers import WallpapersTask
from modules.virtualization import VirtualizationTask
from modules.shell_env import ShellEnvTask
from modules.neovim_dotnet import NeovimDotnetTask
from modules.ides import IdesTask
from modules.dotfiles import DotfilesTask
from modules.git_onboard import GitOnboardTask
from modules.system_tuning import SystemTuningTask
from modules.security import SecurityTask


class TestDryRunPipeline(unittest.TestCase):
    def _create_runner(self, profile: str, enable_dms_niri: bool = False) -> TaskRunner:
        ctx = ExecutionContext.detect(dry_run=True)
        ctx.profile = profile
        ctx.enable_dms_niri = enable_dms_niri
        ctx.enable_nvidia = True
        ctx.install_dev_tools = True
        ctx.enable_gnome_productivity = True
        ctx.enable_wallpapers = True

        state = StateTracker(ctx)
        runner = TaskRunner(ctx, state)

        runner.register(DnfConfigTask())
        runner.register(RepositoriesTask())
        runner.register(MultimediaTask())
        runner.register(NvidiaTask())
        runner.register(PackagesTask())
        runner.register(DevToolsTask())
        runner.register(DesktopGnomeTask())
        runner.register(DesktopDmsNiriTask())
        runner.register(WallpapersTask())
        runner.register(VirtualizationTask())
        runner.register(ShellEnvTask())
        runner.register(NeovimDotnetTask())
        runner.register(IdesTask())
        runner.register(DotfilesTask())
        runner.register(GitOnboardTask())
        runner.register(SystemTuningTask())
        runner.register(SecurityTask())

        return runner

    def test_workstation_dry_run_pipeline(self):
        runner = self._create_runner(profile="workstation", enable_dms_niri=False)
        self.assertEqual(len(runner.tasks), 17)
        success = runner.run_all()
        self.assertTrue(success, "Workstation dry-run pipeline should complete successfully")

    def test_minimal_dry_run_pipeline(self):
        runner = self._create_runner(profile="minimal", enable_dms_niri=True)
        self.assertEqual(len(runner.tasks), 17)
        success = runner.run_all()
        self.assertTrue(success, "Minimal with Niri dry-run pipeline should complete successfully")


if __name__ == "__main__":
    unittest.main()
