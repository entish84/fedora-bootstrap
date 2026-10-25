"""Native IDEs module: JetBrains Toolbox and Visual Studio Code (Native RPM)."""

import json
from pathlib import Path
import urllib.request
from core.context import ExecutionContext
from core.executor import run_root, run_user
from core.logger import logger
from modules.base import BaseTask


class IdesTask(BaseTask):
    name = "ides_install"
    description = "Install native IDEs: JetBrains Toolbox and Visual Studio Code (Native RPM)"

    TOOLBOX_DESKTOP = """[Desktop Entry]
Version=1.0
Type=Application
Name=JetBrains Toolbox
Icon=/opt/jetbrains-toolbox/toolbox.svg
Exec="/usr/local/bin/jetbrains-toolbox" %f
Comment=Manage JetBrains IDEs & Projects
Categories=Development;IDE;
Terminal=false
StartupWMClass=jetbrains-toolbox
"""

    def is_applicable(self, ctx: ExecutionContext) -> bool:
        return any(ide in ctx.selected_ides for ide in ("jetbrains_toolbox", "vscode"))

    def check(self, ctx: ExecutionContext) -> bool:
        ok = True
        if "vscode" in ctx.selected_ides:
            res = run_root("rpm -q code", ctx, check=False, capture=True)
            ok = ok and (res.returncode == 0)
        if "jetbrains_toolbox" in ctx.selected_ides:
            dest_dir = Path("/opt/jetbrains-toolbox")
            has_bin = (
                (dest_dir / "bin" / "jetbrains-toolbox").exists()
                or (dest_dir / "jetbrains-toolbox").exists()
            )
            # Verify symlink is valid and not broken
            symlink = Path("/usr/local/bin/jetbrains-toolbox")
            user_symlink = ctx.target_home / ".local" / "bin" / "jetbrains-toolbox"
            has_valid_symlink = (symlink.is_symlink() and symlink.exists()) or (user_symlink.is_symlink() and user_symlink.exists())

            # Verify icon is installed in Freedesktop icon theme
            has_icon = (
                Path("/usr/share/icons/hicolor/scalable/apps/jetbrains-toolbox.svg").exists()
                or (ctx.target_home / ".local" / "share" / "icons" / "hicolor" / "scalable" / "apps" / "jetbrains-toolbox.svg").exists()
            )

            # Verify desktop launcher exists and specifies correct icon
            desktop_file = Path("/usr/share/applications/jetbrains-toolbox.desktop")
            user_desktop = ctx.target_home / ".local" / "share" / "applications" / "jetbrains-toolbox.desktop"
            has_desktop = False
            for df in (desktop_file, user_desktop):
                if df.exists():
                    try:
                        content = df.read_text(encoding="utf-8")
                        if "Icon=jetbrains-toolbox" in content or "toolbox.svg" in content:
                            has_desktop = True
                            break
                    except Exception:
                        pass

            ok = ok and has_bin and has_valid_symlink and has_icon and has_desktop
        return ok

    def apply(self, ctx: ExecutionContext) -> bool:
        # 1. Native VS Code RPM
        if "vscode" in ctx.selected_ides:
            logger.info("Installing Visual Studio Code via native RPM from Microsoft repository...")
            run_root("dnf install -y code", ctx, check=False)

        # 2. JetBrains Toolbox Native
        if "jetbrains_toolbox" in ctx.selected_ides:
            dest_dir = Path("/opt/jetbrains-toolbox")
            has_bin = (
                (dest_dir / "bin" / "jetbrains-toolbox").exists()
                or (dest_dir / "jetbrains-toolbox").exists()
            )
            if not has_bin:
                logger.info("Fetching latest JetBrains Toolbox release information...")
                dl_url = None
                try:
                    api_url = "https://data.services.jetbrains.com/products/releases?code=TBA&latest=true&type=release"
                    with urllib.request.urlopen(api_url, timeout=10) as resp:
                        data = json.loads(resp.read().decode())
                        dl_url = data.get("TBA", [{}])[0].get("downloads", {}).get("linux", {}).get("link")
                except Exception as e:
                    logger.warning(f"Could not query JetBrains API: {e}")

                if dl_url:
                    logger.info(f"Downloading JetBrains Toolbox from: {dl_url}...")
                    run_root(f"mkdir -p '{dest_dir}'", ctx, check=False)
                    tarball = "/tmp/jetbrains-toolbox.tar.gz"
                    run_root(f"curl -fsSL '{dl_url}' -o {tarball}", ctx, check=False)
                    run_root(f"tar -xzf {tarball} -C '{dest_dir}' --strip-components=1", ctx, check=False)
                    run_root(f"rm -f {tarball}", ctx, check=False)

            # Resolve actual binary location (root vs bin/ subdirectory)
            actual_bin = (
                dest_dir / "bin" / "jetbrains-toolbox"
                if (dest_dir / "bin" / "jetbrains-toolbox").exists()
                else dest_dir / "jetbrains-toolbox"
            )
            # Resolve actual icon location
            actual_icon = (
                dest_dir / "bin" / "toolbox.svg"
                if (dest_dir / "bin" / "toolbox.svg").exists()
                else dest_dir / "toolbox.svg"
            )

            if actual_bin.exists() or ctx.dry_run:
                run_root(f"chmod -R 755 '{dest_dir}'", ctx, check=False)
                run_root(f"ln -sfn '{actual_bin}' /usr/local/bin/jetbrains-toolbox", ctx, check=False)
                run_user(f"mkdir -p '{ctx.target_home}/.local/bin' && ln -sfn '{actual_bin}' '{ctx.target_home}/.local/bin/jetbrains-toolbox'", ctx, check=False)

                # Install icon to system & user hicolor icon themes and pixmaps
                run_root(f"mkdir -p /usr/share/icons/hicolor/scalable/apps /usr/share/pixmaps", ctx, check=False)
                run_root(f"cp -f '{actual_icon}' /usr/share/icons/hicolor/scalable/apps/jetbrains-toolbox.svg", ctx, check=False)
                run_root(f"cp -f '{actual_icon}' /usr/share/pixmaps/jetbrains-toolbox.svg", ctx, check=False)
                run_root(f"ln -sfn '{actual_icon}' '{dest_dir}/toolbox.svg'", ctx, check=False)

                user_icon_dir = ctx.target_home / ".local" / "share" / "icons" / "hicolor" / "scalable" / "apps"
                run_user(f"mkdir -p '{user_icon_dir}' && cp -f '{actual_icon}' '{user_icon_dir}/jetbrains-toolbox.svg'", ctx, check=False)

                # Create desktop shortcut for both system and user
                desktop_content = """[Desktop Entry]
Version=1.0
Type=Application
Name=JetBrains Toolbox
Icon=jetbrains-toolbox
Exec=/usr/local/bin/jetbrains-toolbox %f
Comment=Manage JetBrains IDEs & Projects
Categories=Development;IDE;
Terminal=false
StartupWMClass=jetbrains-toolbox
"""
                if not ctx.dry_run:
                    desktop_file = Path("/usr/share/applications/jetbrains-toolbox.desktop")
                    desktop_file.write_text(desktop_content, encoding="utf-8")
                    desktop_file.chmod(0o644)

                    user_desktop_dir = ctx.target_home / ".local" / "share" / "applications"
                    user_desktop_dir.mkdir(parents=True, exist_ok=True)
                    user_desktop = user_desktop_dir / "jetbrains-toolbox.desktop"
                    user_desktop.write_text(desktop_content.replace("/usr/local/bin/jetbrains-toolbox", str(actual_bin)), encoding="utf-8")
                    user_desktop.chmod(0o644)
                    run_root(f"chown {ctx.target_user}:{ctx.target_user} '{user_desktop}'", ctx, check=False)

                # Update icon caches & desktop databases
                run_root("gtk-update-icon-cache -f -t /usr/share/icons/hicolor || true", ctx, check=False)
                run_user("gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor 2>/dev/null || true", ctx, check=False)
                run_root("update-desktop-database /usr/share/applications || true", ctx, check=False)
                run_user("update-desktop-database ~/.local/share/applications 2>/dev/null || true", ctx, check=False)

                # Restore SELinux context
                run_root("restorecon -R /opt/jetbrains-toolbox /usr/local/bin/jetbrains-toolbox /usr/share/applications/jetbrains-toolbox.desktop /usr/share/icons/hicolor/scalable/apps/jetbrains-toolbox.svg || true", ctx, check=False)

        return True
