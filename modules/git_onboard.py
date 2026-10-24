"""Git configuration and onboarding defaults module."""

from core.context import ExecutionContext
from core.executor import run_user
from core.logger import logger
from modules.base import BaseTask


class GitOnboardTask(BaseTask):
    name = "git_onboard"
    description = "Configure Git defaults (init.defaultBranch main, pull.rebase, core.editor)"

    def is_applicable(self, ctx: ExecutionContext) -> bool:
        return ctx.enable_git_onboard

    def check(self, ctx: ExecutionContext) -> bool:
        res = run_user("git config --global init.defaultBranch", ctx, check=False, capture=True)
        return res.returncode == 0 and res.stdout.strip() == "main"

    def apply(self, ctx: ExecutionContext) -> bool:
        logger.info("Applying modern Git default settings for user...")
        run_user("git config --global init.defaultBranch main", ctx, check=False)
        run_user("git config --global pull.rebase true", ctx, check=False)
        run_user("git config --global push.autoSetupRemote true", ctx, check=False)
        run_user("git config --global core.editor micro", ctx, check=False)
        return True
