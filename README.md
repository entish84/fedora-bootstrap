# Fedora Linux 44 Post-Installation & Developer Bootstrapper

A modern, robust, and idempotent Python 3 system provisioning tool designed for Fedora Linux 44.

## Key Features

- **Dual Profile Provisioning**:
  - **Workstation (GNOME)**: Full desktop workflow, Wayland integration, Papirus icons, MS core fonts, GNOME productivity extensions, **Omakub-inspired keyboard shortcuts & 6 fixed workspaces**, and multimedia codecs.
  - **Minimal (Base System)**: Lean CLI/TUI environment with an interactive option to install **DankLinux Shell with Niri** (DMS, Niri Wayland compositor, Quickshell, Matugen).
- **Mandatory AMD Hardware Acceleration**: Full Mesa Freeworld hardware decoding (`mesa-va-drivers-freeworld`, `mesa-vdpau-drivers-freeworld`) and full FFmpeg freeworld codec swap installed unconditionally across both profiles.
- **Optional NVIDIA Drivers**: Interactive prompt or CLI flag to compile and install RPM Fusion's `akmod-nvidia` and CUDA drivers.
- **Terra-First Package Strategy**: Leverages Fyra Labs' Terra repository for modern CLI/TUI utilities, runtimes, and desktop tools (`mise`, `starship`, `atuin`, `eza`, `bat`, `yazi`, `btop`, `fastfetch`, `niri`, `matugen`, `lazygit`, `lazydocker`).
- **Native RPM IDEs & JetBrains Toolbox**:
  - VS Code installed natively via official Microsoft RPM repository.
  - JetBrains Toolbox automated native installation to `/opt/jetbrains-toolbox` with desktop integration and icon caches for Rider, Android Studio, and CLion without Flatpaks.
  - Neovim with LazyVim pre-configured with a complete `.NET 10` C# toolchain (`mason-org/mason.nvim`, Roslyn/OmniSharp LSP, NetCoreDbg DAP, CSharpier formatting).
- **Dual Dotfiles Engine**:
  - Clones your GitHub dotfiles repository (`https://github.com/<user>/<repo>.git`).
  - Bundles a production-ready fallback dotfiles suite (`.zshrc`, `.zsh_aliases`, `kitty.conf`, `current-theme.conf`, `starship.toml`) with Charcoal-Amber theme.
  - Safe, non-destructive backup (`~/.dotfiles_backup_<timestamp>/`) before symlinking.
- **Minimal Wallpaper Pack**: Clones curated Catppuccin / Minimalist backgrounds from GitHub into `~/Pictures/Wallpapers/` and automatically applies them to GNOME or Niri/DMS.
- **Strict Idempotency & Journaling**: Persistent state tracking at `/var/lib/fedora-bootstrap/state.json`.

---

## Command-Line Options Reference

| Flag / Option | Description | Default |
| :--- | :--- | :--- |
| `--profile {workstation,minimal}` | Target profile: `workstation` (GNOME) or `minimal` (CLI / Niri) | Prompted / Interactive |
| `--dry-run` | Simulate operations and print plan without making any system changes | `False` |
| `--non-interactive` | Run unattended without interactive wizard prompts | `False` |
| `-f`, `--force` | Force re-execution of all tasks from start, ignoring existing state journal | `False` |
| `--dotfiles REPO` | GitHub repository (e.g. `username/dotfiles` or full HTTPS URL) | Prompted / Fallback suite |
| `--with-nvidia` | Enable compilation and installation of `akmod-nvidia` and CUDA drivers | `False` |
| `--with-niri` | Install DankLinux Shell with Niri Wayland compositor (minimal profile) | `False` |
| `--state-file PATH` | Custom location for state tracking journal | `/var/lib/fedora-bootstrap/state.json` |
| `--log-file PATH` | Custom location for execution logs | `/var/log/fedora_bootstrap.log` |
| `-h`, `--help` | Show command-line help message and exit | |

---

## Usage Commands & Recipes

### 1. Interactive Mode (Recommended)
Launches the interactive terminal UI wizard to choose profiles, hardware drivers, IDEs, and dotfiles:
```bash
sudo ./bootstrap.py
```

### 2. Safe Dry-Run Simulation (No Root Required)
Test the entire pipeline safely in simulation mode without root privileges and without modifying your system:
```bash
# General dry-run (interactive prompts)
./bootstrap.py --dry-run

# Workstation profile dry-run
./bootstrap.py --dry-run --profile workstation --non-interactive

# Minimal profile with Niri compositor dry-run
./bootstrap.py --dry-run --profile minimal --with-niri --non-interactive
```

### 3. Unattended Workstation Profile
Install full GNOME desktop environment, multimedia codecs, native IDEs, and developer tools:
```bash
# Standard Workstation (AMD hardware acceleration)
sudo ./bootstrap.py --non-interactive --profile workstation

# Workstation with NVIDIA proprietary drivers
sudo ./bootstrap.py --non-interactive --profile workstation --with-nvidia

# Workstation with custom GitHub dotfiles
sudo ./bootstrap.py --non-interactive --profile workstation --dotfiles yourusername/dotfiles
```

### 4. Unattended Minimal Profile
```bash
# Lean CLI/TUI base system (no heavy desktop environment)
sudo ./bootstrap.py --non-interactive --profile minimal

# Minimal system with DankLinux Shell (DMS) + Niri Wayland compositor
sudo ./bootstrap.py --non-interactive --profile minimal --with-niri
```

---

## State Management & Reset Commands

The bootstrapper records each successfully completed task in an idempotency journal at `/var/lib/fedora-bootstrap/state.json`. Subsequent runs skip already completed tasks.

### Force Full Re-Execution
To re-run all 17 tasks regardless of previous success without manually deleting files:
```bash
sudo ./bootstrap.py --force
# or
sudo ./bootstrap.py -f --profile workstation
```

### Reset State (Start Fresh)
To completely delete the recorded state journal and force the runner to execute all tasks from task 1:
```bash
# Remove the system state journal
sudo rm -f /var/lib/fedora-bootstrap/state.json

# Run bootstrap from the beginning
sudo ./bootstrap.py --profile workstation
```

### Inspect Recorded State
Check which tasks have already been completed on this machine:
```bash
cat /var/lib/fedora-bootstrap/state.json | jq .
```
*(If `jq` is not installed, use `cat /var/lib/fedora-bootstrap/state.json` or `python3 -m json.tool /var/lib/fedora-bootstrap/state.json`)*.

### Use an Alternate State File
Isolate runs or test different pipeline configurations with a custom state journal:
```bash
sudo ./bootstrap.py --state-file /tmp/test-state.json
```

---

## Logging & Diagnostics

The bootstrapper provides dual logging: formatted output in the terminal and detailed debug logging written to disk.

### Live Root Log
When running with `sudo`, logs are saved to `/var/log/fedora_bootstrap.log`:
```bash
# Stream live logs in another terminal
sudo tail -f /var/log/fedora_bootstrap.log

# Search for errors or warnings in log
sudo grep -E "ERROR|WARNING" /var/log/fedora_bootstrap.log
```

### Dry-Run / Unprivileged User Log
When running without `sudo` (e.g. `--dry-run`), logs automatically fall back to the user's local share:
```bash
cat ~/.local/share/fedora-bootstrap/fedora_bootstrap.log
# or
tail -f ~/.local/share/fedora-bootstrap/fedora_bootstrap.log
```

### Custom Log File Path
Specify a custom destination for log output:
```bash
sudo ./bootstrap.py --log-file /tmp/bootstrap_run.log
```

---

## Post-Installation & Verification Commands

After running the bootstrap script, you can verify your system components with the following commands:

### 1. AMD Hardware Acceleration
Verify VA-API and VDPAU drivers are functioning:
```bash
vainfo
vdpauinfo
```

### 2. Developer Runtimes & Tools
```bash
# Shell & Version Managers
zsh --version
mise --version
dotnet --version

# Modern CLI/TUI utilities
lazygit --version
lazydocker --version
yazi --version
starship --version
fastfetch
```

### 3. Native IDEs & Neovim
```bash
# JetBrains Toolbox & VS Code
which jetbrains-toolbox
which code

# Neovim with LazyVim & .NET 10
nvim
# Inside Neovim, check plugin and LSP status:
# :Lazy
# :Mason
```

### 4. Docker Permissions
Verify Docker access without needing a full system reboot:
```bash
newgrp docker
docker ps
```

### 5. Memory & ZRAM
Verify ZRAM compression configuration:
```bash
zramctl
```

### 6. GNOME Omakub Keyboard Shortcuts
Verify custom workspace management and shortcuts:
```bash
# Check custom keybindings
gsettings get org.gnome.desktop.wm.keybindings switch-to-workspace-1
gsettings get org.gnome.desktop.wm.keybindings move-to-workspace-1
gsettings get org.gnome.mutter dynamic-workspaces
```

---

## Automated Unit Tests

The test suite runs in sandbox mode and does not modify the host system:
```bash
python3 -m unittest discover tests
```

To run individual test cases:
```bash
python3 -m unittest tests.test_syntax_and_imports
python3 -m unittest tests.test_context_and_state
python3 -m unittest tests.test_dotfiles_sandbox
python3 -m unittest tests.test_dry_run_pipeline
```

---

## Project Structure

```
fedora-bootstrap/
├── bootstrap.py                 # Main CLI runner
├── dotfiles_fallback/           # Bundled fallback dotfiles (Charcoal-Amber suite)
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
│   ├── state.py                 # Idempotency journal (state.json)
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
│   ├── desktop_gnome.py         # GNOME settings, Papirus icons, extensions, Omakub shortcuts
│   ├── desktop_dms_niri.py      # Minimal: Niri compositor, DMS, Quickshell, Matugen
│   ├── wallpapers.py            # GitHub minimal wallpapers & theme hook
│   ├── virtualization.py        # Docker-CE, Podman, KVM user groups
│   ├── shell_env.py             # Zsh default shell, Zinit, Mise runtimes (.NET 10)
│   ├── neovim_dotnet.py         # LazyVim with .NET 10 LSP/DAP (mason-org)
│   ├── ides.py                  # JetBrains Toolbox & native VS Code RPM
│   ├── dotfiles.py              # GitHub clone OR Fallback symlinking
│   ├── git_onboard.py           # Git defaults onboarding
│   ├── system_tuning.py         # ZRAM memory tuning
│   └── security.py              # SSH server & ed25519 keypair
└── tests/                       # Unit tests & isolated sandbox tests
```
