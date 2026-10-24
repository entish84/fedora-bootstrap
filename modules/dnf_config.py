"""DNF5 configuration and optimization module."""

from pathlib import Path
from core.context import ExecutionContext
from core.executor import run_root
from core.logger import logger
from modules.base import BaseTask


class DnfConfigTask(BaseTask):
    name = "dnf_config"
    description = "Configure DNF5 optimizations (parallel downloads, fastest mirror)"

    DNF5_CONF = Path("/etc/dnf/dnf5.conf")
    DNF_CONF = Path("/etc/dnf/dnf.conf")

    CONFIG_CONTENT = """[main]
gpgcheck=True
installonly_limit=3
clean_requirements_on_remove=True
skip_if_unavailable=True
max_parallel_downloads=10
defaultyes=True
"""

    def is_applicable(self, ctx: ExecutionContext) -> bool:
        return True

    def check(self, ctx: ExecutionContext) -> bool:
        target = self.DNF5_CONF if self.DNF5_CONF.exists() else self.DNF_CONF
        if not target.exists():
            return False
        try:
            content = target.read_text(encoding="utf-8")
            return "max_parallel_downloads=10" in content and "defaultyes=True" in content
        except Exception:
            return False

    def apply(self, ctx: ExecutionContext) -> bool:
        # Write to both dnf5.conf and dnf.conf for broad compatibility
        for conf_path in (self.DNF5_CONF, self.DNF_CONF):
            if ctx.dry_run:
                logger.debug(f"[DRY-RUN] Writing optimized config to {conf_path}")
            else:
                conf_path.parent.mkdir(parents=True, exist_ok=True)
                conf_path.write_text(self.CONFIG_CONTENT, encoding="utf-8")

        # Clean cache
        run_root("dnf clean all", ctx, check=False)
        return True
