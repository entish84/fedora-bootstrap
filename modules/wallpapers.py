"""Minimal wallpapers bootstrapper and dynamic theme integration."""

from pathlib import Path
from core.context import ExecutionContext
from core.executor import run_user
from core.logger import logger
from modules.base import BaseTask


class WallpapersTask(BaseTask):
    name = "wallpapers_setup"
    description = "Bootstrap minimal wallpapers from GitHub and apply dynamic desktop theming"

    REPO_URL = "https://github.com/zhichaoh/catppuccin-wallpapers.git"

    def is_applicable(self, ctx: ExecutionContext) -> bool:
        return ctx.enable_wallpapers

    def check(self, ctx: ExecutionContext) -> bool:
        wallpapers_dir = ctx.target_home / "Pictures" / "Wallpapers"
        if not (wallpapers_dir.exists() and any(wallpapers_dir.iterdir())):
            return False
        if ctx.profile == "workstation":
            res = run_user("gsettings get org.gnome.desktop.background picture-uri", ctx, check=False, capture=True)
            if "catppuccin" not in res.stdout:
                return False
        return True

    def apply(self, ctx: ExecutionContext) -> bool:
        target_dir = ctx.target_home / ".local" / "share" / "backgrounds" / "catppuccin"
        pictures_symlink = ctx.target_home / "Pictures" / "Wallpapers"

        logger.info(f"Cloning minimal wallpapers repository into {target_dir}...")
        cmd = f"git clone --depth 1 {self.REPO_URL} '{target_dir}' || true"
        run_user(cmd, ctx, check=False, capture=False)

        # Create symlink ~/Pictures/Wallpapers
        symlink_cmd = f"mkdir -p '{pictures_symlink.parent}' && ln -sfn '{target_dir}' '{pictures_symlink}'"
        run_user(symlink_cmd, ctx, check=False)

        # Pick a default dark wallpaper
        default_wp = None
        if not ctx.dry_run and target_dir.exists():
            for candidate in target_dir.glob("**/*.png"):
                if "dark" in candidate.name.lower() or "mocha" in candidate.name.lower() or "minimal" in str(candidate).lower():
                    default_wp = candidate
                    break
            if not default_wp:
                pngs = list(target_dir.glob("**/*.png"))
                if pngs:
                    default_wp = pngs[0]

        if default_wp:
            wp_uri = f"file://{default_wp}"
            if ctx.profile == "workstation":
                logger.info(f"Setting GNOME desktop wallpaper to: {default_wp.name}")
                run_user(f"gsettings set org.gnome.desktop.background picture-uri '{wp_uri}'", ctx, check=False)
                run_user(f"gsettings set org.gnome.desktop.background picture-uri-dark '{wp_uri}'", ctx, check=False)

            if ctx.enable_dms_niri:
                logger.info(f"Generating Matugen color palette from: {default_wp.name}")
                run_user(f"matugen image '{default_wp}' || true", ctx, check=False)

        return True
