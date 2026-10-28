"""Multimedia codecs and mandatory AMD GPU hardware acceleration module."""

from core.context import ExecutionContext
from core.executor import run_root
from core.logger import logger
from modules.base import BaseTask


class MultimediaTask(BaseTask):
    name = "multimedia_codecs"
    description = "Install mandatory AMD GPU hardware codecs and universal multimedia stack"

    def is_applicable(self, ctx: ExecutionContext) -> bool:
        return ctx.enable_amd_codecs

    def check(self, ctx: ExecutionContext) -> bool:
        # Check if freeworld packages are active
        res = run_root("rpm -q mesa-va-drivers-freeworld ffmpeg", ctx, check=False, capture=True)
        return res.returncode == 0

    def apply(self, ctx: ExecutionContext) -> bool:
        logger.info("Swapping to full FFmpeg and Freeworld Mesa drivers (AMD hardware acceleration)...")

        # 1. FFmpeg Full swap
        run_root("dnf swap -y ffmpeg-free ffmpeg --allowerasing || dnf install -y ffmpeg", ctx, check=False, capture=False)

        # 2. AMD Hardware accelerated drivers
        run_root("dnf swap -y mesa-va-drivers mesa-va-drivers-freeworld", ctx, check=False, capture=False)
        run_root("dnf swap -y mesa-vdpau-drivers mesa-vdpau-drivers-freeworld", ctx, check=False, capture=False)

        # 3. Multimedia groups
        logger.info("Installing multimedia and audio packages...")
        run_root('dnf update -y @multimedia --setopt="install_weak_deps=False" --exclude=PackageKit-gstreamer-plugin,libheif-freeworld', ctx, check=False, capture=False)
        run_root("dnf update -y @sound-and-video --exclude=libheif-freeworld", ctx, check=False, capture=False)

        # 4. PipeWire & WirePlumber
        # run_root("dnf install -y pipewire wireplumber pipewire-pulseaudio pipewire-alsa pipewire-gstreamer", ctx, check=False, capture=False)

        return True
