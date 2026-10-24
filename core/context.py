"""Execution context and configuration management for the Fedora 44 bootstrapper."""

from dataclasses import dataclass, field
import os
import pwd
import sys
from pathlib import Path
from typing import List, Optional


@dataclass
class ExecutionContext:
    """Carries runtime parameters, user identity, and feature selections across all tasks."""

    # Target user identity
    target_user: str
    target_uid: int
    target_gid: int
    target_home: Path

    # Core profile: 'workstation' (GNOME) or 'minimal' (Base CLI/TUI)
    profile: str = "workstation"

    # Hardware & Compositor toggles
    enable_amd_codecs: bool = True  # Mandatory
    enable_nvidia: bool = False     # Optional
    enable_dms_niri: bool = False   # Minimal profile option

    # Desktop & Customization
    enable_gnome_productivity: bool = True
    enable_wallpapers: bool = True
    enable_git_onboard: bool = True
    enable_zram_tuning: bool = True

    # Software & IDE selection
    selected_ides: List[str] = field(default_factory=lambda: ["jetbrains_toolbox", "vscode", "neovim"])
    install_docker: bool = True
    install_podman: bool = True
    install_dev_tools: bool = True

    # Dotfiles configuration
    dotfiles_repo: Optional[str] = None
    use_fallback_dotfiles: bool = True

    # Script control flags
    dry_run: bool = False
    non_interactive: bool = False
    state_file: Path = Path("/var/lib/fedora-bootstrap/state.json")
    log_file: Path = Path("/var/log/fedora_bootstrap.log")
    project_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent)

    @classmethod
    def detect(cls, dry_run: bool = False) -> "ExecutionContext":
        """Detect the actual running user (invoked with sudo) and resolve home paths."""
        sudo_user = os.environ.get("SUDO_USER")
        if sudo_user:
            try:
                pw = pwd.getpwnam(sudo_user)
                user = pw.pw_name
                uid = pw.pw_uid
                gid = pw.pw_gid
                home = Path(pw.pw_dir)
            except KeyError:
                user = sudo_user
                uid = int(os.environ.get("SUDO_UID", "1000"))
                gid = int(os.environ.get("SUDO_GID", "1000"))
                home = Path(f"/home/{user}")
        else:
            # Fallback if run directly by user or in mock/test environment
            user = os.environ.get("USER", "fedora")
            uid = os.getuid()
            gid = os.getgid()
            home = Path.home()

        return cls(
            target_user=user,
            target_uid=uid,
            target_gid=gid,
            target_home=home,
            dry_run=dry_run
        )
