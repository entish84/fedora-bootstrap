"""Modern lean Neovim with Microsoft Roslyn .NET 10, Polyglot LSP, and Catppuccin theme."""

from pathlib import Path
import shutil
from core.context import ExecutionContext
from core.executor import run_root
from core.logger import logger
from modules.base import BaseTask


class NeovimDotnetTask(BaseTask):
    name = "neovim_dotnet"
    description = "Bootstrap modern lean Neovim with Microsoft Roslyn .NET 10 and Polyglot LSP"

    def is_applicable(self, ctx: ExecutionContext) -> bool:
        return "neovim" in ctx.selected_ides

    def check(self, ctx: ExecutionContext) -> bool:
        nvim_dir = ctx.target_home / ".config" / "nvim"
        dotnet_plugin = nvim_dir / "lua" / "plugins" / "dotnet.lua"
        init_file = nvim_dir / "init.lua"
        if not init_file.exists() or not dotnet_plugin.exists():
            return False
        try:
            content = dotnet_plugin.read_text(encoding="utf-8")
            return "seblyng/roslyn.nvim" in content
        except Exception:
            return False

    def apply(self, ctx: ExecutionContext) -> bool:
        logger.info("Installing Neovim from Terra/Fedora...")
        run_root("dnf install -y neovim", ctx, check=False, capture=False)

        nvim_dir = ctx.target_home / ".config" / "nvim"
        source_nvim = ctx.project_dir / "dotfiles_fallback" / ".config" / "nvim"

        logger.info("Deploying self-contained modern lean Neovim configuration...")
        if not ctx.dry_run and source_nvim.exists():
            nvim_dir.mkdir(parents=True, exist_ok=True)
            # Remove legacy LazyVim artifacts if present
            legacy_files = [
                nvim_dir / "lazyvim.json",
                nvim_dir / ".neoconf.json",
                nvim_dir / "stylua.toml",
            ]
            for lf in legacy_files:
                if lf.exists():
                    try:
                        lf.unlink()
                    except Exception:
                        pass

            # Copy all files from bundled source template
            shutil.copytree(source_nvim, nvim_dir, dirs_exist_ok=True)

        # Fix ownership to target user (run with root to handle any root-owned files)
        run_root(f"chown -R {ctx.target_user}:{ctx.target_user} '{nvim_dir}'", ctx, check=False)
        return True
