"""Optional NVIDIA proprietary drivers and CUDA module."""

from core.context import ExecutionContext
from core.executor import run_root
from core.logger import logger
from modules.base import BaseTask


class NvidiaTask(BaseTask):
    name = "nvidia_drivers"
    description = "Install NVIDIA proprietary drivers (akmod-nvidia) and CUDA support"

    def is_applicable(self, ctx: ExecutionContext) -> bool:
        return ctx.enable_nvidia

    def check(self, ctx: ExecutionContext) -> bool:
        res = run_root("rpm -q akmod-nvidia", ctx, check=False, capture=True)
        return res.returncode == 0

    def apply(self, ctx: ExecutionContext) -> bool:
        logger.info("Installing NVIDIA drivers from RPM Fusion Nonfree...")
        run_root("dnf install -y akmod-nvidia xorg-x11-drv-nvidia-cuda", ctx, check=True, capture=False)
        logger.info("Compiling kernel modules via akmods...")
        run_root("akmods --force", ctx, check=False, capture=False)
        return True
