"""Native IDEs module: JetBrains Toolbox and Visual Studio Code (Native RPM)."""

import json
from pathlib import Path
import urllib.request
from core.context import ExecutionContext
from core.executor import run_root
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
            ok = ok and Path("/opt/jetbrains-toolbox/jetbrains-toolbox").exists()
        return ok

    def apply(self, ctx: ExecutionContext) -> bool:
        # 1. Native VS Code RPM
        if "vscode" in ctx.selected_ides:
            logger.info("Installing Visual Studio Code via native RPM from Microsoft repository...")
            run_root("dnf install -y code", ctx, check=False)

        # 2. JetBrains Toolbox Native
        if "jetbrains_toolbox" in ctx.selected_ides:
            dest_dir = Path("/opt/jetbrains-toolbox")
            bin_path = dest_dir / "jetbrains-toolbox"
            if not bin_path.exists():
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

                    # Extract/find icon or binary
                    run_root("chmod -R 755 /opt/jetbrains-toolbox", ctx, check=False)
                    run_root("ln -sfn /opt/jetbrains-toolbox/jetbrains-toolbox /usr/local/bin/jetbrains-toolbox", ctx, check=False)

                    # Create desktop shortcut
                    if not ctx.dry_run:
                        desktop_file = Path("/usr/share/applications/jetbrains-toolbox.desktop")
                        desktop_file.write_text(self.TOOLBOX_DESKTOP, encoding="utf-8")
                        desktop_file.chmod(0o644)

                    # Restore SELinux context
                    run_root("restorecon -R /opt/jetbrains-toolbox /usr/local/bin/jetbrains-toolbox /usr/share/applications/jetbrains-toolbox.desktop", ctx, check=False)
                    run_root("update-desktop-database /usr/share/applications || true", ctx, check=False)

        return True
