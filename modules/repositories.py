"""Repository configuration module: Terra, RPM Fusion, Flathub, Docker, Microsoft."""

from pathlib import Path
from core.context import ExecutionContext
from core.executor import run_root
from core.logger import logger
from modules.base import BaseTask


class RepositoriesTask(BaseTask):
    name = "repositories_setup"
    description = "Configure Terra, RPM Fusion, Flathub, Docker, and Microsoft repositories"

    TERRA_REPO = Path("/etc/yum.repos.d/terra.repo")
    VSCODE_REPO = Path("/etc/yum.repos.d/vscode.repo")
    DOCKER_REPO = Path("/etc/yum.repos.d/docker-ce.repo")

    TERRA_CONTENT = """[terra]
name=Terra $releasever
baseurl=https://repos.fyralabs.com/terra$releasever
enabled=1
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-terra$releasever
skip_if_unavailable=True
zchunk=False
metadata_expire=1h
"""

    VSCODE_CONTENT = """[code]
name=Visual Studio Code
baseurl=https://packages.microsoft.com/yumrepos/vscode
enabled=1
autorefresh=1
type=rpm-md
gpgcheck=1
gpgkey=https://packages.microsoft.com/keys/microsoft.asc
skip_if_unavailable=True
"""

    def is_applicable(self, ctx: ExecutionContext) -> bool:
        return True

    def check(self, ctx: ExecutionContext) -> bool:
        return self.TERRA_REPO.exists() and self.VSCODE_REPO.exists() and self.DOCKER_REPO.exists()

    def apply(self, ctx: ExecutionContext) -> bool:
        # Clean legacy or broken repos
        for old_repo in ("/etc/yum.repos.d/mise.repo",):
            p = Path(old_repo)
            if p.exists() and not ctx.dry_run:
                p.unlink()

        # 1. Terra Repository (Fyra Labs) - Primary source
        logger.info("Setting up Terra repository...")
        run_root(
            "dnf install -y --nogpgcheck --repofrompath terra-bootstrap,https://repos.fyralabs.com/terra$releasever terra-release",
            ctx,
            check=False
        )
        run_root("rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-terra*", ctx, check=False)
        if not ctx.dry_run:
            self.TERRA_REPO.write_text(self.TERRA_CONTENT, encoding="utf-8")

        # 2. RPM Fusion Free & Nonfree
        logger.info("Setting up RPM Fusion repositories...")
        run_root(
            "dnf install -y https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm "
            "https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm",
            ctx,
            check=False
        )

        # 3. Flathub (for Workstation or if Flatpak apps are selected)
        if ctx.profile == "workstation" or any(a in ctx.selected_apps for a in ("obsidian", "github_desktop")):
            logger.info("Configuring Flathub...")
            run_root("dnf install -y flatpak", ctx, check=False)
            run_root("flatpak remote-delete fedora --force", ctx, check=False)
            run_root("flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo", ctx, check=False)

        # 4. Microsoft VS Code Repo
        logger.info("Configuring Visual Studio Code repository...")
        run_root("rpm --import https://packages.microsoft.com/keys/microsoft.asc", ctx, check=False)
        if not ctx.dry_run:
            self.VSCODE_REPO.write_text(self.VSCODE_CONTENT, encoding="utf-8")

        # 5. Docker CE Repo
        logger.info("Configuring Docker CE repository...")
        run_root(
            "curl -fsSL https://download.docker.com/linux/fedora/docker-ce.repo -o /etc/yum.repos.d/docker-ce.repo",
            ctx,
            check=False
        )

        return True
