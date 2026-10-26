"""Optional modern applications module (Antigravity CLI, LibreOffice, Waydroid, GitHub Desktop, LocalSend, Zen Browser, Zed Editor, Ollama, Bruno, Vesktop, Obsidian)."""

import json
from pathlib import Path
import shutil
from typing import Dict, List
from core.context import ExecutionContext
from core.executor import run_root, run_user
from core.logger import logger
from modules.base import BaseTask


class OptionalAppsTask(BaseTask):
    name = "optional_apps"
    description = "Install user-selected modern desktop, developer, and AI applications"

    APP_PACKAGES: Dict[str, List[str]] = {
        "zen": ["zen-browser"],
        "zed": ["zed", "zed-cli"],
        "localsend": ["localsend-bin"],
        "ollama": ["ollama"],
        "libreoffice": ["libreoffice", "libreoffice-gtk4"],
        "waydroid": ["waydroid", "lxc", "scrcpy"],
        "bruno": ["bruno"],
        "vesktop": ["vesktop"],
    }

    def is_applicable(self, ctx: ExecutionContext) -> bool:
        return bool(ctx.selected_apps)

    def check(self, ctx: ExecutionContext) -> bool:
        if not ctx.selected_apps:
            return True

        for app in ctx.selected_apps:
            if app == "antigravity":
                agy_bin = ctx.target_home / ".local" / "bin" / "agy"
                if not agy_bin.exists() and not shutil.which("agy"):
                    return False
            elif app == "github_desktop":
                res_rpm = run_root("rpm -q github-desktop", ctx, check=False, capture=True)
                res_flatpak = run_user("flatpak info io.github.shiftey.Desktop", ctx, check=False, capture=True)
                if res_rpm.returncode != 0 and res_flatpak.returncode != 0:
                    return False
            elif app == "obsidian":
                res = run_user("flatpak info md.obsidian.Obsidian", ctx, check=False, capture=True)
                if res.returncode != 0:
                    return False
            elif app in self.APP_PACKAGES:
                pkgs = self.APP_PACKAGES[app]
                check_str = " ".join(pkgs)
                res = run_root(f"rpm -q {check_str}", ctx, check=False, capture=True)
                if res.returncode != 0:
                    return False

        return True

    def _configure_zed_assistant(self, ctx: ExecutionContext) -> None:
        """Pre-configure Zed Editor with Ollama Assistant and Language Models."""
        zed_dir = ctx.target_home / ".config" / "zed"
        settings_file = zed_dir / "settings.json"

        default_settings = {
            "theme": "One Dark",
            "ui_font_size": 15,
            "buffer_font_size": 14,
            "buffer_font_family": "FiraCode Nerd Font",
            "terminal": {
                "font_family": "FiraCode Nerd Font",
                "shell": {
                    "program": "/usr/sbin/zsh"
                }
            },
            "assistant": {
                "version": "2",
                "default_model": {
                    "provider": "ollama",
                    "model": "qwen2.5-coder:7b"
                }
            },
            "language_models": {
                "ollama": {
                    "api_url": "http://localhost:11434",
                    "context_window": 16384,
                    "auto_discover": True
                }
            }
        }

        if not ctx.dry_run:
            zed_dir.mkdir(parents=True, exist_ok=True)
            if settings_file.exists():
                try:
                    data = json.loads(settings_file.read_text(encoding="utf-8"))
                    data["assistant"] = default_settings["assistant"]
                    data["language_models"] = default_settings["language_models"]
                    settings_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
                except Exception:
                    settings_file.write_text(json.dumps(default_settings, indent=2), encoding="utf-8")
            else:
                settings_file.write_text(json.dumps(default_settings, indent=2), encoding="utf-8")

            run_root(f"chown -R {ctx.target_user}:{ctx.target_user} '{zed_dir}'", ctx, check=False)

    def apply(self, ctx: ExecutionContext) -> bool:
        # 1. Batch native RPM packages from Terra and Fedora
        rpm_pkgs: List[str] = []
        for app in ctx.selected_apps:
            if app in self.APP_PACKAGES:
                rpm_pkgs.extend(self.APP_PACKAGES[app])

        if rpm_pkgs:
            logger.info(f"Downloading and installing selected native RPM applications: {' '.join(rpm_pkgs)}...")
            run_root(f"dnf install -y --skip-unavailable {' '.join(rpm_pkgs)}", ctx, check=False, capture=False)

        # 2. Antigravity CLI via official script
        if "antigravity" in ctx.selected_apps:
            agy_bin = ctx.target_home / ".local" / "bin" / "agy"
            if not agy_bin.exists():
                logger.info("Installing Antigravity CLI (agy) via official Google installer...")
                run_user("curl -fsSL https://antigravity.google/cli/install.sh | bash", ctx, check=False, capture=False)

            if agy_bin.exists() or ctx.dry_run:
                run_root(f"ln -sfn '{agy_bin}' /usr/local/bin/agy", ctx, check=False)

        # 3. GitHub Desktop via Flathub (with fallback to direct GitHub release RPM)
        if "github_desktop" in ctx.selected_apps:
            res_rpm = run_root("rpm -q github-desktop", ctx, check=False, capture=True)
            res_flatpak = run_user("flatpak info io.github.shiftey.Desktop", ctx, check=False, capture=True)
            if res_rpm.returncode != 0 and res_flatpak.returncode != 0:
                logger.info("Installing GitHub Desktop from Flathub...")
                res = run_user("flatpak install -y flathub io.github.shiftey.Desktop", ctx, check=False, capture=False)
                if res.returncode != 0:
                    logger.info("Flathub install failed; falling back to official GitHub release RPM...")
                    rpm_url = "https://github.com/shiftkey/desktop/releases/download/release-3.4.13-linux1/GitHubDesktop-linux-x86_64-3.4.13-linux1.rpm"
                    run_root(f"dnf install -y '{rpm_url}'", ctx, check=False, capture=False)

            # Ensure CLI executable /usr/local/bin/github-desktop exists for terminal/alias access
            if not shutil.which("github-desktop") and not ctx.dry_run:
                run_root(
                    "printf '#!/bin/bash\\nexec flatpak run io.github.shiftey.Desktop \"$@\"\\n' > /usr/local/bin/github-desktop && chmod 755 /usr/local/bin/github-desktop",
                    ctx,
                    check=False
                )

        # 4. Obsidian via Flatpak
        if "obsidian" in ctx.selected_apps:
            res_obs = run_user("flatpak info md.obsidian.Obsidian", ctx, check=False, capture=True)
            if res_obs.returncode != 0:
                logger.info("Installing Obsidian from Flathub...")
                run_user("flatpak install -y flathub md.obsidian.Obsidian", ctx, check=False, capture=False)

        # 5. Service Configuration: Ollama
        if "ollama" in ctx.selected_apps:
            logger.info("Enabling and starting Ollama background daemon...")
            run_root("systemctl enable --now ollama", ctx, check=False)
            logger.info("Ollama API service active at http://localhost:11434.")
            logger.info("To pull the recommended coding model, run: ollama pull qwen2.5-coder:7b")

        # 6. Zed Editor Assistant Configuration
        if "zed" in ctx.selected_apps:
            logger.info("Configuring Zed Editor with native Ollama Assistant and FiraCode Nerd Font...")
            self._configure_zed_assistant(ctx)

        # 7. Service Configuration: Waydroid
        if "waydroid" in ctx.selected_apps:
            logger.info("Enabling Waydroid LXC container service...")
            run_root("systemctl enable waydroid-container", ctx, check=False)
            logger.info("Waydroid container service ready. Initialize anytime with: waydroid init")

        return True
