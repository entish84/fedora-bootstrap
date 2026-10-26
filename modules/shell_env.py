"""Shell environment setup: Zsh default shell, Zinit bootstrap, and Mise runtimes."""

from pathlib import Path
from core.context import ExecutionContext
from core.executor import run_root, run_user
from core.logger import logger
from modules.base import BaseTask


class ShellEnvTask(BaseTask):
    name = "shell_environment"
    description = "Configure Zsh as default shell, pre-clone Zinit, and setup Mise runtimes"

    def is_applicable(self, ctx: ExecutionContext) -> bool:
        return True

    def check(self, ctx: ExecutionContext) -> bool:
        zinit_dir = ctx.target_home / ".local" / "share" / "zinit" / "zinit.git"
        return zinit_dir.exists()

    def apply(self, ctx: ExecutionContext) -> bool:
        # 1. Ensure Zsh is default shell
        logger.info(f"Setting default login shell to Zsh for {ctx.target_user}...")
        res = run_root("which zsh", ctx, check=False, capture=True)
        zsh_bin = res.stdout.strip() if res.success and res.stdout else "/bin/zsh"
        run_root(f"usermod -s {zsh_bin} {ctx.target_user}", ctx, check=False)

        # 2. Pre-clone Zinit into user's local share
        zinit_dir = ctx.target_home / ".local" / "share" / "zinit" / "zinit.git"
        if not zinit_dir.exists():
            logger.info("Pre-cloning Zinit plugin manager...")
            cmd = f"mkdir -p '{zinit_dir.parent}' && git clone https://github.com/zdharma-continuum/zinit.git '{zinit_dir}' || true"
            run_user(cmd, ctx, check=False, capture=False)

        # 3. Setup Mise global runtimes (.NET 10, Node LTS, Java LTS)
        logger.info("Configuring Mise polyglot runtime manager (.NET 10, Node LTS, Java LTS)...")
        run_root("dnf install -y mise", ctx, check=False, capture=False)

        run_user("mise settings set idiomatic_version_file false 2>/dev/null || true", ctx, check=False)
        run_user("mise settings set yes true 2>/dev/null || true", ctx, check=False)
        run_user("mise use --global dotnet@10 node@lts java@lts 2>/dev/null || true", ctx, check=False)

        return True
