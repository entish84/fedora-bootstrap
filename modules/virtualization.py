"""Containers and virtualization module (Docker CE, Podman, and KVM user groups)."""

from core.context import ExecutionContext
from core.executor import run_root
from core.logger import logger
from modules.base import BaseTask


class VirtualizationTask(BaseTask):
    name = "virtualization_setup"
    description = "Install Docker CE, Podman, and configure user permissions for Docker and KVM"

    def is_applicable(self, ctx: ExecutionContext) -> bool:
        return ctx.install_docker or ctx.install_podman

    def check(self, ctx: ExecutionContext) -> bool:
        res = run_root("which docker podman", ctx, check=False, capture=True)
        return res.returncode == 0

    def apply(self, ctx: ExecutionContext) -> bool:
        # 1. Install Docker CE
        if ctx.install_docker:
            logger.info("Installing Docker CE and Compose plugin...")
            res = run_root(
                "dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin",
                ctx,
                check=False,
                capture=False
            )
            if not res.success:
                logger.warning("Docker CE install failed, falling back to moby-engine...")
                run_root("dnf install -y moby-engine docker-compose", ctx, check=False, capture=False)

            # Enable and start services
            run_root("systemctl enable --now docker", ctx, check=False)
            run_root("systemctl enable --now containerd", ctx, check=False)

        # 2. Install Podman
        if ctx.install_podman:
            logger.info("Installing Podman...")
            run_root("dnf install -y podman", ctx, check=False, capture=False)

        # 3. User Group Permissions (docker & kvm)
        logger.info(f"Adding user '{ctx.target_user}' to docker and kvm groups...")
        run_root("getent group docker >/dev/null || groupadd docker", ctx, check=False)
        run_root("getent group kvm >/dev/null || groupadd kvm", ctx, check=False)
        run_root(f"usermod -aG docker,kvm {ctx.target_user}", ctx, check=False)

        return True
