"""Developer TUI tools, Jujutsu, and UV package manager."""

from core.context import ExecutionContext
from core.executor import run_root
from core.logger import logger
from modules.base import BaseTask


class DevToolsTask(BaseTask):
    name = "dev_tools"
    description = "Install developer productivity tools: lazygit, lazydocker, jujutsu, uv, tealdeer"

    TOOLS = [
        "lazygit",
        "lazydocker",
        "tealdeer",
        "duf",
        "dust",
        "procs",
        "jujutsu",
        "uv"
    ]

    def is_applicable(self, ctx: ExecutionContext) -> bool:
        return ctx.install_dev_tools

    def check(self, ctx: ExecutionContext) -> bool:
        res = run_root("which lazygit lazydocker jj uv", ctx, check=False, capture=True)
        return res.returncode == 0

    def apply(self, ctx: ExecutionContext) -> bool:
        tool_str = " ".join(self.TOOLS)
        logger.info(f"Installing developer TUI tools from Terra/Fedora: {tool_str}...")
        run_root(f"dnf install -y --skip-unavailable {tool_str}", ctx, check=False)

        # Initialize tealdeer cache
        run_root("tldr --update || true", ctx, check=False)
        return True
