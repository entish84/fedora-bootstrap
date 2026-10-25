"""GNOME desktop customization, Papirus icon theme, productivity extensions, and Omakub keyboard shortcuts."""

from core.context import ExecutionContext
from core.executor import run_root, run_user
from core.logger import logger
from modules.base import BaseTask


class DesktopGnomeTask(BaseTask):
    name = "desktop_gnome"
    description = "Configure GNOME Workstation theming, Papirus icons, extensions, and Omakub keyboard shortcuts"

    EXTENSIONS = [
        "gnome-shell-extension-appindicator",
        "gnome-shell-extension-dash-to-dock",
        "gnome-shell-extension-blur-my-shell",
        "gnome-shell-extension-caffeine"
    ]

    def is_applicable(self, ctx: ExecutionContext) -> bool:
        return ctx.profile == "workstation"

    def check(self, ctx: ExecutionContext) -> bool:
        # Verify papirus theme package is installed
        res = run_root("rpm -q papirus-icon-theme", ctx, check=False, capture=True)
        if res.returncode != 0:
            return False

        # Verify icon theme setting in GSettings
        theme_res = run_user("gsettings get org.gnome.desktop.interface icon-theme", ctx, check=False, capture=True)
        if "'Papirus'" not in theme_res.stdout:
            return False

        # If productivity is enabled, verify Omakub shortcuts and workspace count
        if ctx.enable_gnome_productivity:
            sc_res = run_user("gsettings get org.gnome.desktop.wm.keybindings close", ctx, check=False, capture=True)
            if "['<Super>w']" not in sc_res.stdout:
                return False

            ws_res = run_user("gsettings get org.gnome.desktop.wm.preferences num-workspaces", ctx, check=False, capture=True)
            if "6" not in ws_res.stdout:
                return False

        return True

    def _apply_omakub_shortcuts(self, ctx: ExecutionContext) -> None:
        """Apply keyboard-driven workflow shortcuts inspired by Omakub."""
        logger.info("Applying Omakub-inspired GNOME keyboard shortcuts and workspace management...")

        # 1. Window Management Shortcuts
        # Super+W to close window (replaces Alt+F4)
        run_user("gsettings set org.gnome.desktop.wm.keybindings close \"['<Super>w']\"", ctx, check=False)
        # Super+Up to maximize window
        run_user("gsettings set org.gnome.desktop.wm.keybindings maximize \"['<Super>Up']\"", ctx, check=False)
        # Super+BackSpace to resize undecorated windows
        run_user("gsettings set org.gnome.desktop.wm.keybindings begin-resize \"['<Super>BackSpace']\"", ctx, check=False)
        # Shift+F11 for fullscreen with titlebar
        run_user("gsettings set org.gnome.desktop.wm.keybindings toggle-fullscreen \"['<Shift>F11']\"", ctx, check=False)
        # Shift+AudioPlay for next music track (for MX Keys style keyboards)
        run_user("gsettings set org.gnome.settings-daemon.plugins.media-keys next \"['<Shift>AudioPlay']\"", ctx, check=False)

        # 2. 6 Fixed Workspaces (instead of dynamic workspaces)
        run_user("gsettings set org.gnome.mutter dynamic-workspaces false", ctx, check=False)
        run_user("gsettings set org.gnome.desktop.wm.preferences num-workspaces 6", ctx, check=False)

        # 3. Super + 1-6 to Switch Workspaces, Super + Shift + 1-6 to Move Windows
        for i in range(1, 7):
            run_user(f"gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-{i} \"['<Super>{i}']\"", ctx, check=False)
            run_user(f"gsettings set org.gnome.desktop.wm.keybindings move-to-workspace-{i} \"['<Super><Shift>{i}']\"", ctx, check=False)

        # 4. Alt + 1-9 for Pinned Dock Applications (releasing Super + 1-6 for workspaces)
        run_user("gsettings set org.gnome.shell.extensions.dash-to-dock hot-keys false", ctx, check=False)
        for i in range(1, 10):
            run_user(f"gsettings set org.gnome.shell.keybindings switch-to-application-{i} \"['<Alt>{i}']\"", ctx, check=False)

        # 5. Custom Keybindings: Super + Return for Kitty Terminal
        custom_path = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/"
        run_user(f"gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings \"['{custom_path}']\"", ctx, check=False)
        run_user(f"gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:{custom_path} name 'Kitty Terminal'", ctx, check=False)
        run_user(f"gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:{custom_path} command 'kitty'", ctx, check=False)
        run_user(f"gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:{custom_path} binding '<Super>Return'", ctx, check=False)

        # 6. Ergonomics & Display Tweaks
        # Turn off ambient light sensors (stops screen brightness flickering)
        run_user("gsettings set org.gnome.settings-daemon.plugins.power ambient-enabled false", ctx, check=False)
        # Show week numbers in calendar
        run_user("gsettings set org.gnome.desktop.calendar show-weekdate true", ctx, check=False)
        # Set system monospace font to FiraCode Nerd Font
        run_user("gsettings set org.gnome.desktop.interface monospace-font-name 'FiraCode Nerd Font 11'", ctx, check=False)

    def apply(self, ctx: ExecutionContext) -> bool:
        logger.info("Installing Papirus icon theme...")
        run_root("dnf install -y papirus-icon-theme", ctx, check=False)

        # Set Papirus icon theme for target user
        run_user("gsettings set org.gnome.desktop.interface icon-theme 'Papirus'", ctx, check=False)

        if ctx.enable_gnome_productivity:
            logger.info("Installing GNOME productivity extensions...")
            ext_str = " ".join(self.EXTENSIONS)
            run_root(f"dnf install -y --skip-unavailable {ext_str}", ctx, check=False)

            logger.info("Applying GNOME productivity GSettings tweaks...")
            # 1. Add minimize/maximize buttons
            run_user("gsettings set org.gnome.desktop.wm.preferences button-layout 'appmenu:minimize,maximize,close'", ctx, check=False)
            # 2. Center new windows
            run_user("gsettings set org.gnome.mutter center-new-windows true", ctx, check=False)
            # 3. Prefer dark theme
            run_user("gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'", ctx, check=False)
            # 4. Touchpad tap-to-click
            run_user("gsettings set org.gnome.desktop.peripherals.touchpad tap-to-click true", ctx, check=False)

            # 5. Apply Omakub Keyboard Shortcuts & Workspace Configuration
            self._apply_omakub_shortcuts(ctx)

        return True
