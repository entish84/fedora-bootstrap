"""Dotfiles management engine with GitHub integration, non-destructive backup, and symlinking."""

from pathlib import Path
import shutil
import time
from core.context import ExecutionContext
from core.executor import run_root, run_user
from core.logger import logger
from modules.base import BaseTask


class DotfilesTask(BaseTask):
    name = "dotfiles_setup"
    description = "Deploy user dotfiles from GitHub or bundled fallback suite with safe backups"

    def is_applicable(self, ctx: ExecutionContext) -> bool:
        return True

    def check(self, ctx: ExecutionContext) -> bool:
        zshrc = ctx.target_home / ".zshrc"
        return zshrc.is_symlink() and ".dotfiles" in str(zshrc.resolve())

    def apply(self, ctx: ExecutionContext) -> bool:
        dotfiles_dir = ctx.target_home / ".dotfiles"
        timestamp = int(time.time())
        backup_dir = ctx.target_home / f".dotfiles_backup_{timestamp}"

        # 1. Source dotfiles: Remote Git Repo vs Bundled Fallback
        if ctx.dotfiles_repo:
            repo_url = ctx.dotfiles_repo
            if not repo_url.startswith("http") and not repo_url.startswith("git@"):
                repo_url = f"https://github.com/{repo_url}.git"
            logger.info(f"Cloning user dotfiles from GitHub ({repo_url})...")
            cmd = f"rm -rf '{dotfiles_dir}' && git clone '{repo_url}' '{dotfiles_dir}'"
            run_user(cmd, ctx, check=False)
        else:
            logger.info("Using bundled Charcoal-Amber fallback dotfiles suite...")
            fallback_source = ctx.project_dir / "dotfiles_fallback"
            if not ctx.dry_run and fallback_source.exists():
                dotfiles_dir.mkdir(parents=True, exist_ok=True)
                for item in fallback_source.iterdir():
                    dest = dotfiles_dir / item.name
                    if item.is_dir():
                        shutil.copytree(item, dest, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, dest)

        # 2. File mappings to symlink
        mappings = [
            (".zshrc", ctx.target_home / ".zshrc"),
            (".zsh_aliases", ctx.target_home / ".zsh_aliases"),
            (".config/kitty/kitty.conf", ctx.target_home / ".config" / "kitty" / "kitty.conf"),
            (".config/kitty/current-theme.conf", ctx.target_home / ".config" / "kitty" / "current-theme.conf"),
            (".config/starship.toml", ctx.target_home / ".config" / "starship.toml"),
        ]

        # 3. Non-destructive backup and symlinking
        for rel_src, dest_path in mappings:
            src_file = dotfiles_dir / rel_src
            if not src_file.exists():
                continue

            if dest_path.exists() or dest_path.is_symlink():
                # If already correctly symlinked, skip
                if dest_path.is_symlink() and dest_path.resolve() == src_file.resolve():
                    continue

                logger.info(f"Backing up existing file: {dest_path} -> {backup_dir}")
                if not ctx.dry_run:
                    backup_dir.mkdir(parents=True, exist_ok=True)
                    rel_backup = backup_dir / rel_src
                    rel_backup.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(dest_path), str(rel_backup))

            logger.info(f"Symlinking: {dest_path} -> {src_file}")
            if not ctx.dry_run:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                dest_path.symlink_to(src_file)

        # 4. Fix permissions
        run_root(f"chown -R {ctx.target_user}:{ctx.target_user} '{dotfiles_dir}'", ctx, check=False)
        if backup_dir.exists():
            run_root(f"chown -R {ctx.target_user}:{ctx.target_user} '{backup_dir}'", ctx, check=False)
        return True
