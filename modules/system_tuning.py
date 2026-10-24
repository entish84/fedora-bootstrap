"""System performance, ZRAM tuning, and memory optimization module."""

from pathlib import Path
from core.context import ExecutionContext
from core.executor import run_root
from core.logger import logger
from modules.base import BaseTask


class SystemTuningTask(BaseTask):
    name = "system_tuning"
    description = "Configure ZRAM memory compression (zstd) for high-performance builds"

    ZRAM_CONF = Path("/etc/systemd/zram-generator.conf")
    ZRAM_CONTENT = """[zram0]
zram-size = ram
compression-algorithm = zstd
swap-priority = 100
"""

    def is_applicable(self, ctx: ExecutionContext) -> bool:
        return ctx.enable_zram_tuning

    def check(self, ctx: ExecutionContext) -> bool:
        if not self.ZRAM_CONF.exists():
            return False
        try:
            return "compression-algorithm = zstd" in self.ZRAM_CONF.read_text()
        except Exception:
            return False

    def apply(self, ctx: ExecutionContext) -> bool:
        logger.info("Configuring high-performance ZRAM generator with zstd compression...")
        if not ctx.dry_run:
            self.ZRAM_CONF.parent.mkdir(parents=True, exist_ok=True)
            self.ZRAM_CONF.write_text(self.ZRAM_CONTENT, encoding="utf-8")

        run_root("systemctl daemon-reload && systemctl restart /dev/zram0 || true", ctx, check=False)
        return True
