"""Core system tools, compilers, CLI utilities, and Nerd fonts installation module."""

from core.context import ExecutionContext
from core.executor import run_root
from core.logger import logger
from modules.base import BaseTask


class PackagesTask(BaseTask):
    name = "packages_core"
    description = "Install core build tools, modern CLI/TUI utilities, and Nerd fonts"

    CORE_PACKAGES = [
        # Compilers & core build tools
        "git", "curl", "wget", "tar", "unzip", "p7zip", "p7zip-plugins", "jq",
        "make", "cmake", "clang", "ninja-build",
        # Modern CLI / TUI tools
        "eza", "bat", "fzf", "ripgrep", "fd-find", "zoxide", "yazi",
        "direnv", "micro", "btop", "fastfetch", "inxi", "wl-clipboard", "poppler-utils",
        "zsh", "kitty",
        # Typography & Nerd Fonts
        "firacode-nerd-fonts", "rsms-inter-vf-fonts", "0xproto-nerd-fonts",
        "cabextract", "fontconfig"
    ]

    def is_applicable(self, ctx: ExecutionContext) -> bool:
        return True

    def check(self, ctx: ExecutionContext) -> bool:
        # Check a representative sample of modern tools (note: binary for ripgrep is 'rg')
        res = run_root("which eza bat fzf rg zoxide yazi micro", ctx, check=False, capture=True)
        return res.returncode == 0

    def apply(self, ctx: ExecutionContext) -> bool:
        logger.info("Performing system upgrade and installing core packages...")
        run_root("dnf upgrade --refresh -y", ctx, check=False)

        pkg_str = " ".join(self.CORE_PACKAGES)
        logger.info(f"Installing {len(self.CORE_PACKAGES)} core packages & fonts...")
        run_root(f"dnf install -y --skip-unavailable {pkg_str}", ctx, check=False)

        # Refresh font cache
        run_root("fc-cache -f", ctx, check=False)
        return True
