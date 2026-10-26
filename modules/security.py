"""SSH server setup, user ed25519 key generation, and Wayland clipboard integration."""

from pathlib import Path
from core.context import ExecutionContext
from core.executor import run_root, run_user
from core.logger import logger
from modules.base import BaseTask


class SecurityTask(BaseTask):
    name = "security_setup"
    description = "Configure SSH server, generate ed25519 keypair, and integrate with Wayland clipboard"

    def is_applicable(self, ctx: ExecutionContext) -> bool:
        return True

    def check(self, ctx: ExecutionContext) -> bool:
        key_file = ctx.target_home / ".ssh" / "id_ed25519"
        return key_file.exists()

    def apply(self, ctx: ExecutionContext) -> bool:
        # 1. Enable OpenSSH server
        logger.info("Enabling and starting OpenSSH server daemon...")
        run_root("dnf install -y openssh-server", ctx, check=False, capture=False)
        run_root("systemctl enable --now sshd", ctx, check=False)

        # 2. Generate ed25519 keypair for user
        ssh_dir = ctx.target_home / ".ssh"
        key_file = ssh_dir / "id_ed25519"
        pub_key_file = ssh_dir / "id_ed25519.pub"

        if not key_file.exists():
            logger.info("Generating user ed25519 SSH keypair...")
            cmd = f"mkdir -p '{ssh_dir}' && chmod 700 '{ssh_dir}' && ssh-keygen -t ed25519 -f '{key_file}' -N ''"
            run_user(cmd, ctx, check=False)

            # Copy to clipboard if wl-clipboard is available
            run_user(f"wl-copy < '{pub_key_file}' 2>/dev/null || true", ctx, check=False)

        if not ctx.dry_run and pub_key_file.exists():
            try:
                pub_key = pub_key_file.read_text().strip()
                logger.info(f"SSH Public Key: {pub_key}")
            except Exception:
                pass

        return True
