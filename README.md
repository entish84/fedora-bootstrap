# Fedora Linux 44 Post-Installation & Developer Bootstrapper

A modern, robust, and idempotent Python 3 system provisioning tool designed for Fedora Linux 44.

## Key Features

- **Dual Profile Provisioning**:
  - **Workstation (GNOME)**: Full desktop workflow, Wayland integration, Papirus icons, MS core fonts, GNOME productivity extensions, **Omakub-inspired keyboard shortcuts & 6 fixed workspaces**, and multimedia codecs.
  - **Minimal (Base System)**: Lean CLI/TUI environment with an interactive option to install **DankLinux Shell with Niri** (DMS, Niri Wayland compositor, Quickshell, Matugen).
- **Mandatory AMD Hardware Acceleration**: Full Mesa Freeworld hardware decoding (`mesa-va-drivers-freeworld`, `mesa-vdpau-drivers-freeworld`) and full FFmpeg freeworld codec swap installed unconditionally across both profiles.
- **Optional NVIDIA Drivers**: Interactive prompt to compile and install RPM Fusion's `akmod-nvidia` and CUDA drivers.
- **Terra-First Package Strategy**: Leverages Fyra Labs' Terra repository for modern CLI/TUI utilities, runtimes, and desktop tools (`mise`, `starship`, `atuin`, `eza`, `bat`, `yazi`, `btop`, `fastfetch`, `niri`, `matugen`, `lazygit`, `lazydocker`).
- **Native RPM IDEs & JetBrains Toolbox**:
  - VS Code installed natively via official Microsoft RPM repository.
  - JetBrains Toolbox automated native installation to `/opt/jetbrains-toolbox` to manage Rider, Android Studio, and CLion without Flatpaks.
  - Neovim with LazyVim pre-configured with a complete `.NET 10` C# toolchain (Roslyn/OmniSharp LSP, NetCoreDbg DAP, CSharpier formatting, Mason).
- **Dual Dotfiles Engine**:
  - Prompts for your GitHub dotfiles repository (`https://github.com/<user>/<repo>.git`).
  - Bundles your production-ready fallback dotfiles suite (`.zshrc`, `.zsh_aliases`, `kitty.conf`, `current-theme.conf`, `starship.toml`) with Charcoal-Amber theme.
  - Safe, non-destructive backup (`~/.dotfiles_backup_<timestamp>/`) before symlinking.
- **Minimal Wallpaper Pack**: Clones curated Catppuccin / Minimalist backgrounds from GitHub into `~/Pictures/Wallpapers/` and automatically applies them to GNOME or Niri/DMS.
- **Strict Idempotency**: Persistent state tracking at `/var/lib/fedora-bootstrap/state.json`.

---

## Quick Start

### 1. Interactive Execution (Recommended)
Run the bootstrapper with `sudo`:
```bash
sudo ./bootstrap.py
```

### 2. Safe Dry-Run Simulation (No system changes)
You can test the entire pipeline safely without modifying your live system:
```bash
./bootstrap.py --dry-run
```

### 3. Non-Interactive Unattended Mode
```bash
sudo ./bootstrap.py --non-interactive --profile workstation --dotfiles yourusername/dotfiles
```

---

## Project Structure

```
fedora-bootstrap/
├── bootstrap.py                 # Main CLI runner
├── dotfiles_fallback/           # Bundled fallback dotfiles
│   ├── .zshrc
│   ├── .zsh_aliases
│   └── .config/
│       ├── kitty/
│       │   ├── kitty.conf
│       │   └── current-theme.conf
│       └── starship.toml
├── core/
│   ├── context.py               # Runtime context & user detection
│   ├── executor.py              # Privilege separation (root vs user) & runner
│   ├── state.py                 # Idempotency journal
│   ├── ui.py                    # Terminal UI & prompts
│   └── logger.py                # Dual logger (terminal + logfile)
├── modules/
│   ├── base.py                  # BaseTask & TaskRunner
│   ├── dnf_config.py            # DNF5 optimizations
│   ├── repositories.py          # Terra, RPM Fusion, Flathub, Docker, MS
│   ├── multimedia.py            # AMD VA-API/VDPAU & FFmpeg freeworld
│   ├── nvidia.py                # Optional akmod-nvidia installer
│   ├── packages.py              # Base compilers, CLI/TUI tools, Nerd fonts
│   ├── dev_tools.py             # lazygit, lazydocker, tealdeer, duf, procs, jj, uv
│   ├── desktop_gnome.py         # GNOME settings, Papirus icons, extensions
│   ├── desktop_dms_niri.py      # Minimal: Niri compositor, DMS, Quickshell, Matugen
│   ├── wallpapers.py            # GitHub minimal wallpapers & theme hook
│   ├── virtualization.py        # Docker-CE, Podman, KVM user groups
│   ├── shell_env.py             # Zsh default shell, Zinit, Mise runtimes (.NET 10)
│   ├── neovim_dotnet.py         # LazyVim with .NET 10 LSP/DAP
│   ├── ides.py                  # JetBrains Toolbox & native VS Code RPM
│   ├── dotfiles.py              # GitHub clone OR Fallback symlinking
│   ├── git_onboard.py           # Git defaults onboarding
│   ├── system_tuning.py         # ZRAM memory tuning
│   └── security.py              # SSH server & ed25519 keypair
└── tests/                       # Unit tests & isolated sandbox tests
```
