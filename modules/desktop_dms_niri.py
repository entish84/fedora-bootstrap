"""Minimal profile desktop module: DankLinux Shell with Niri Wayland compositor."""

from core.context import ExecutionContext
from core.executor import run_root
from core.logger import logger
from modules.base import BaseTask


class DesktopDmsNiriTask(BaseTask):
    name = "desktop_dms_niri"
    description = "Install DankLinux Shell with Niri Wayland compositor, Matugen, and Quickshell"

    PACKAGES = [
        "niri",
        "dms",
        "matugen",
        "quickshell",
        "waybar",
        "fuzzel",
        "wl-clipboard",
        "swaybg",
        "mako",
        "xdg-desktop-portal-gnome",
        "xdg-desktop-portal-gtk"
    ]

    def is_applicable(self, ctx: ExecutionContext) -> bool:
        return ctx.profile == "minimal" and ctx.enable_dms_niri

    def check(self, ctx: ExecutionContext) -> bool:
        res = run_root("which niri matugen", ctx, check=False, capture=True)
        return res.returncode == 0

    def apply(self, ctx: ExecutionContext) -> bool:
        logger.info("Enabling DMS Copr repository...")
        run_root("dnf copr enable -y avengemedia/dms-git", ctx, check=False, capture=False)

        pkg_str = " ".join(self.PACKAGES)
        logger.info(f"Installing Niri, DankMaterialShell, and Wayland utilities: {pkg_str}...")
        run_root(f"dnf install -y --skip-unavailable {pkg_str}", ctx, check=False, capture=False)

        # Create user config directories
        niri_dir = ctx.target_home / ".config" / "niri"
        dms_dir = ctx.target_home / ".config" / "dms"
        if not ctx.dry_run:
            niri_dir.mkdir(parents=True, exist_ok=True)
            dms_dir.mkdir(parents=True, exist_ok=True)

        return True
