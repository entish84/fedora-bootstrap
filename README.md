# Fedora Linux 44 Post-Installation & Developer Bootstrapper

A modern, robust, and idempotent Python 3 system provisioning tool designed for Fedora Linux 44.

## Key Features

- **Dual Profile Provisioning**:
  - **Workstation (GNOME)**: Full desktop workflow, Wayland integration, Papirus icons, MS core fonts, GNOME productivity extensions, **Omakub-inspired keyboard shortcuts & 6 fixed workspaces**, and multimedia codecs.
  - **Minimal (Base System)**: Lean CLI/TUI environment with an interactive option to install **DankLinux Shell with Niri** (DMS, Niri Wayland compositor, Quickshell, Matugen).
  - **KDE Plasma Spin Compatibility**: The `minimal` profile can be run on Fedora 44 KDE Spin with **zero conflicts**, preserving SDDM and Plasma while installing the complete developer runtime stack.
- **Mandatory AMD Hardware Acceleration**: Full Mesa Freeworld hardware decoding (`mesa-va-drivers-freeworld`, `mesa-vdpau-drivers-freeworld`) and full FFmpeg freeworld codec swap installed unconditionally across all profiles.
- **Optional NVIDIA Drivers**: Interactive prompt or CLI flag (`--with-nvidia`) to compile and install RPM Fusion's `akmod-nvidia` and CUDA drivers.
- **Terra-First Package Strategy**: Leverages Fyra Labs' Terra repository for modern CLI/TUI utilities, runtimes, and desktop tools (`mise`, `starship`, `atuin`, `eza`, `bat`, `yazi`, `btop`, `fastfetch`, `niri`, `matugen`, `lazygit`, `lazydocker`).
- **Optional Modern Applications & Local AI Suite**:
  - Interactive multi-select checkbox UI and CLI flag (`--apps` / `--no-apps`) to install modern tools.
  - **Google Antigravity CLI** (`agy`): Installed via official Google installer into `~/.local/bin/agy`.
  - **Zen Browser** & **Zed Editor**: Native RPMs via Terra repository with custom Ollama assistant pre-configured.
  - **Ollama**: Native RPM daemon with systemd service enabled for local LLM inference.
  - **LocalSend**: Cross-platform, local network AirDrop alternative via Terra.
  - **LibreOffice**: Full office productivity suite with GTK4 integration via official Fedora repositories.
  - **Android on Linux (Waydroid & Scrcpy)**: Native containerized Android execution and physical device mirroring.
  - **GitHub Desktop**: Native RPM packaged via ShiftKey repository.
  - **Bruno, Vesktop, Obsidian**: Modern API client, Discord client, and knowledge base.
- **Native RPM IDEs & JetBrains Toolbox**:
  - VS Code installed natively via official Microsoft RPM repository.
  - JetBrains Toolbox automated native installation to `/opt/jetbrains-toolbox` with desktop integration and icon caches for Rider, Android Studio, and CLion without Flatpaks.
  - **Modern Lean Neovim Native Pack** (<20ms startup): Built on Neovim 0.12 native LSP & lazy.nvim with Catppuccin Mocha theme, Which-Key v3 popup help (`<leader>?`), Blink.cmp (sub-2ms completion), Fzf-Lua, and a polyglot language toolchain (Official Microsoft Roslyn LSP for .NET 10 / C#, Pyright/Ruff for Python, ts_ls/Prettier for JS/TS/HTML/CSS, rust-analyzer for Rust, Marksman + render-markdown for Markdown).
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
| `--profile {workstation,minimal}` | Target profile: `workstation` (GNOME) or `minimal` (CLI / Niri / KDE) | Prompted / Interactive |
| `--dry-run` | Simulate operations and print plan without making any system changes | `False` |
| `--non-interactive` | Run unattended without interactive wizard prompts | `False` |
| `-f`, `--force` | Force re-execution of all tasks from start, ignoring existing state journal | `False` |
| `--apps APPS` | Comma-separated list of optional apps (`antigravity`, `zen`, `zed`, `localsend`, `ollama`, `libreoffice`, `waydroid`, `github_desktop`, `bruno`, `vesktop`, `obsidian`) or `all`/`none` | Prompted / Interactive |
| `--no-apps` | Skip installation of all optional desktop and AI applications | `False` |
| `--dotfiles REPO` | GitHub repository (e.g. `username/dotfiles` or full HTTPS URL) | Prompted / Fallback suite |
| `--with-nvidia` | Enable compilation and installation of `akmod-nvidia` and CUDA drivers | `False` |
| `--with-niri` | Install DankLinux Shell with Niri Wayland compositor (minimal profile) | `False` |
| `--state-file PATH` | Custom location for state tracking journal | `/var/lib/fedora-bootstrap/state.json` |
| `--log-file PATH` | Custom location for execution logs | `/var/log/fedora_bootstrap.log` |
| `-h`, `--help` | Show command-line help message and exit | |

---

## Usage Commands & Recipes

### 1. Interactive Mode (Recommended)
Launches the interactive terminal UI wizard to choose profiles, hardware drivers, IDEs, optional apps, and dotfiles:
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

# Workstation dry-run with all optional apps
./bootstrap.py --dry-run --profile workstation --non-interactive --apps all

# Minimal profile with Niri compositor dry-run
./bootstrap.py --dry-run --profile minimal --with-niri --non-interactive
```

### 3. Unattended Workstation Profile
Install full GNOME desktop environment, multimedia codecs, native IDEs, and developer tools:
```bash
# Standard Workstation with default optional apps (antigravity, zen, zed, localsend, ollama)
sudo ./bootstrap.py --non-interactive --profile workstation

# Workstation with ALL optional applications
sudo ./bootstrap.py --non-interactive --profile workstation --apps all

# Workstation with specific applications
sudo ./bootstrap.py --non-interactive --profile workstation --apps antigravity,zed,ollama,waydroid

# Workstation without any optional apps
sudo ./bootstrap.py --non-interactive --profile workstation --no-apps

# Workstation with NVIDIA proprietary drivers
sudo ./bootstrap.py --non-interactive --profile workstation --with-nvidia

# Workstation with custom GitHub dotfiles
sudo ./bootstrap.py --non-interactive --profile workstation --dotfiles yourusername/dotfiles
```

### 4. Unattended Minimal Profile (CLI or Fedora KDE Spin)
```bash
# Lean CLI/TUI base system (safe for Fedora KDE Spin)
sudo ./bootstrap.py --non-interactive --profile minimal

# Minimal system with DankLinux Shell (DMS) + Niri Wayland compositor
sudo ./bootstrap.py --non-interactive --profile minimal --with-niri
```

---

## Local AI & LLM Environment (Ollama, Zed, Antigravity)

The bootstrap suite installs and pre-configures a private, local-first artificial intelligence development stack.

### Hardware-Optimized Model Recommendations
For systems equipped with an **AMD Ryzen 7 8845HS** (8C/16T Zen 4, AVX-512) and an **NVIDIA GeForce RTX 4050 Laptop GPU (6 GB GDDR6 VRAM)**:

| Model | Size / Quant | Memory Footprint | Primary Use Case | Expected Speed |
| :--- | :--- | :--- | :--- | :--- |
| **`qwen2.5-coder:7b`** *(Top Pick)* | 4.7 GB (Q4_K_M) | ~4.7 GB (100% in VRAM) | General coding, refactoring, architecture, explanations | **35–60+ tokens/sec** |
| **`deepseek-r1:7b`** | 4.7 GB (Q4_K_M) | ~4.7 GB (100% in VRAM) | Complex reasoning, mathematical logic, code debugging | **30–50 tokens/sec** |
| **`qwen2.5-coder:1.5b`** | 986 MB (Q4_K_M) | ~1.0 GB VRAM | Blazing-fast inline autocompletion & syntax suggestions | **90–120+ tokens/sec** |

> [!TIP]
> The `qwen2.5-coder:7b` model fits completely inside the 6 GB RTX 4050 VRAM with ~1.3 GB remaining for KV-cache and desktop compositor overhead. This ensures zero memory swapping to system RAM, giving you instantaneous GPU inference.

### Manual Model Pull Commands
Models are **not** downloaded during bootstrap to save bandwidth and install time. Pull them manually after installation:

```bash
# 1. Verify that the Ollama daemon is active
systemctl status ollama

# 2. Pull the recommended primary coding model (Qwen 2.5 Coder 7B)
ollama pull qwen2.5-coder:7b

# 3. (Optional) Pull the DeepSeek R1 reasoning model
ollama pull deepseek-r1:7b

# 4. (Optional) Pull the ultra-lightweight inline autocomplete model
ollama pull qwen2.5-coder:1.5b

# 5. List all installed local models
ollama list

# 6. Test the model in interactive terminal chat
ollama run qwen2.5-coder:7b
```

### Zed Editor Ollama Integration
When `zed` and `ollama` are selected, the bootstrapper automatically writes `~/.config/zed/settings.json` configuring Ollama as Zed's native AI assistant provider:
- **Default Assistant Provider**: `ollama`
- **Default Model**: `qwen2.5-coder:7b`
- **Context Window**: `16384` tokens
- **API Endpoint**: `http://localhost:11434`

**How to use AI in Zed Editor**:
- <kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>B</kbd>: Toggle the AI Assistant panel on the right.
- <kbd>Ctrl</kbd> + <kbd>Enter</kbd>: Send prompt to your local model.
- Select any code in the editor and press <kbd>Ctrl</kbd> + <kbd>I</kbd> to prompt the local LLM to refactor, write docstrings, or fix bugs directly inline.

### Google Antigravity CLI (`agy`)
When `antigravity` is selected, the official Google Antigravity CLI is installed to `~/.local/bin/agy` and symlinked to `/usr/local/bin/agy`.
```bash
# Launch Antigravity interactive assistant
agy

# Display version and CLI help
agy --version
agy --help
```

---

## Android Applications on Linux (Waydroid & Scrcpy)

When `waydroid` is selected, the bootstrapper installs `waydroid`, `lxc`, and `scrcpy`, and enables the `waydroid-container.service`.

### 1. Initializing Waydroid (First-Time Setup)
Initialize the containerized Android runtime (requires ~1 GB download of LineageOS image):
```bash
# Standard vanilla LineageOS Android 11/13 image
sudo waydroid init

# OR initialize with Google Play Services (GAPPS) support:
# sudo waydroid init -s GAPPS
```

### 2. Running Android Apps
Waydroid runs in multi-window mode on Wayland (GNOME, KDE Plasma, or Niri), allowing Android apps to float as standard desktop windows:
```bash
# Start Waydroid background session
waydroid session start &

# Open the full Android UI launcher
waydroid show-full-ui

# Install an APK from your local machine
waydroid app install /path/to/downloaded-app.apk

# List installed Android applications
waydroid app list

# Launch an app directly by package name
waydroid app launch <com.example.app>

# Stop Waydroid session when finished
waydroid session stop
```

### 3. Physical Android Device Control (Scrcpy)
Control and mirror your physical Android phone with high performance, low latency, and audio forwarding:
```bash
# Connect phone via USB with USB Debugging enabled:
scrcpy

# High-framerate mode with screen turned off to save battery:
scrcpy --max-fps=120 --turn-screen-off --stay-awake

# Wireless debugging over local Wi-Fi:
scrcpy --tcpip
```

---

## Fedora 44 KDE Spin Compatibility Guide

The bootstrapper is fully tested and compatible with **Fedora 44 KDE Spin (Plasma 6 Desktop)**.

### Running Minimal Profile on KDE
To provision a clean Fedora 44 KDE installation with our developer stack, run:
```bash
sudo ./bootstrap.py --profile minimal
```

### Why There Are Zero Conflicts:
1. **Desktop Isolation**: `DesktopGnomeTask` only executes when `--profile workstation`. In the `minimal` profile, all GNOME packages, Mutter, and gsettings commands are completely skipped.
2. **KDE Plasma Intact**: No KDE Plasma configuration files (`~/.config/kdeglobals`, `plasmarc`, `kwinrc`, `plasma-org.kde.plasma.desktop-appletsrc`) are modified or touched.
3. **Display Manager (SDDM)**: If `--with-niri` is selected, the Niri Wayland session descriptor is placed at `/usr/share/wayland-sessions/niri.desktop`. SDDM automatically detects it without altering your default Plasma session. You can switch between Plasma and Niri from the login screen.
4. **Desktop-Agnostic Tools**: DNF5 optimizations, AMD VA-API/VDPAU hardware acceleration, RPM Fusion, Terra, Flathub, Mise (.NET 10, Rust, Node, Go, Python), Docker, Zed, Zen Browser, JetBrains Toolbox, VS Code, and Ollama integrate natively into KDE's Kickoff Application Launcher and system tray via standard Freedesktop `.desktop` files.
5. **Shell & Kitty**: The bundled Zsh and Kitty configuration integrates cleanly with KDE's terminal ecosystem.

---

## Updated `.zsh_aliases` Quick Reference

The bundled fallback dotfiles (`.zsh_aliases`) and repository dotfiles include practical productivity shortcuts:

### Bootstrap Shortcuts
| Alias | Expanded Command | Description |
| :--- | :--- | :--- |
| `fb` | `sudo /home/rs/fedora-bootstrap/bootstrap.py` | Run bootstrap runner with interactive wizard |
| `fb-dry` | `python3 /home/rs/fedora-bootstrap/bootstrap.py --dry-run` | Run dry-run simulation without modifying system |
| `fb-status`| `cat /var/lib/fedora-bootstrap/state.json \| jq .` | Inspect completed tasks and state journal |
| `fb-reset` | `sudo rm -f /var/lib/fedora-bootstrap/state.json` | Reset state to force execution from task 1 |
| `fb-log` | `sudo tail -f /var/log/fedora_bootstrap.log` | Stream live bootstrap execution logs |

### AI & Local LLM Shortcuts
| Alias | Expanded Command | Description |
| :--- | :--- | :--- |
| `agy` | `agy` | Google Antigravity CLI |
| `ol` | `ollama` | Ollama CLI |
| `olr` | `ollama run qwen2.5-coder:7b` | Instant interactive chat with Qwen 2.5 Coder 7B |
| `olls` | `ollama list` | List downloaded local AI models |
| `olps` | `ollama ps` | Display active models in GPU memory |
| `olrm` | `ollama rm` | Remove a local model |

### Android & Device Shortcuts
| Alias | Expanded Command | Description |
| :--- | :--- | :--- |
| `wd` | `waydroid` | Waydroid CLI |
| `wd-start`| `waydroid session start` | Start Waydroid session |
| `wd-stop` | `waydroid session stop` | Stop Waydroid session |
| `wd-show` | `waydroid show-full-ui` | Open Waydroid Android graphical UI |
| `wd-in` | `waydroid app install` | Install an APK (`wd-in app.apk`) |
| `scp` | `scrcpy` | Mirror connected physical Android phone |
| `scp-wifi`| `scrcpy --tcpip` | Connect to physical Android phone over Wi-Fi |

### Modern Applications & Editors
| Alias | Expanded Command | Description |
| :--- | :--- | :--- |
| `v` | `nvim` | Launch Neovim with Modern Lean Native Pack & .NET 10 |
| `z` | `zed` | Launch Zed Editor |
| `zen` | `zen-browser` | Launch Zen Browser |
| `tb` | `jetbrains-toolbox` | Launch JetBrains Toolbox |
| `lsend` | `localsend` | Launch LocalSend |
| `ghd` | `github-desktop` | Launch GitHub Desktop |
| `bruno` | `bruno` | Launch Bruno API client |

### Modern CLI & System Tools
| Alias | Expanded Command | Description |
| :--- | :--- | :--- |
| `top` | `btop` | Modern process and hardware monitor |
| `y` | `yazi` | Fast terminal file manager |
| `du` | `dust` | Graphical disk space analyzer |
| `df` | `duf` | Modern disk usage utility |
| `psg` | `procs` | Enhanced `ps` viewer |
| `lg` | `lazygit` | Terminal UI for Git |
| `lzd` | `lazydocker` | Terminal UI for Docker |

---

## State Management & Reset Commands

The bootstrapper records each successfully completed task in an idempotency journal at `/var/lib/fedora-bootstrap/state.json`. Subsequent runs skip already completed tasks.

### Force Full Re-Execution
To re-run all 18 tasks regardless of previous success without manually deleting files:
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

### 3. Native IDEs, Editors & AI
```bash
# JetBrains Toolbox, VS Code, Zed
which jetbrains-toolbox
which code
which zed
which agy

# Ollama & Service Status
systemctl status ollama
ollama list

# Neovim Modern Lean Native Pack (<20ms startup)
nvim
# Inside Neovim:
#   <Space>          - Leader key (opens which-key menu)
#   <leader>?        - Comprehensive keybinding cheatsheet popup
#   <leader>ff       - Fast fuzzy find files (fzf-lua)
#   <leader>fg       - Live grep in workspace
#   <leader>e        - Fast file tree / directory browser (mini.files)
#   <C-\> / <leader>tt - Toggle floating terminal (toggleterm)
#   <leader>th       - Toggle horizontal bottom terminal drawer
#   -- .NET & Polyglot Run/Build:
#   <leader>rr       - dotnet run (Interactive terminal)
#   <leader>rw       - dotnet watch run (Hot-reload development server)
#   <leader>rb       - dotnet build (Colorized terminal output)
#   <leader>rB       - dotnet build (Neovim Quickfix error navigation)
#   <leader>rt       - dotnet test (Run tests in terminal)
#   <leader>rc       - dotnet clean
#   -- Python Web (uv):
#   <leader>ru       - FastAPI / Uvicorn server (--reload)
#   <leader>rf       - Flask dev server (--debug)
#   <leader>rd       - Django runserver
#   <leader>cv       - Select Python VirtualEnv (venv-selector)
#   -- Web Development (Live Server & Emmet):
#   <leader>ws       - Start Live Server (auto-launches Zen Browser on :5500)
#   <leader>wS       - Stop Live Server
#   <leader>we       - Emmet wrap with abbreviation
#   -- AI Suite (Antigravity agy, CodeCompanion, Minuet):
#   <leader>aa       - Toggle Antigravity AI Agent (Floating TUI)
#   <leader>ac       - Toggle CodeCompanion Chat (Ollama qwen2.5-coder)
#   <leader>ai / ga  - CodeCompanion Inline Assistant (modify selection / generate)
#   <leader>ap       - CodeCompanion Action Palette
#   <leader>ar       - AGY Code Review & Security Audit
#   <leader>ae       - AGY Explain Code
#   <leader>af       - AGY Fix / Refactor Code
#   <leader>ag       - AGY Generate Unit Tests
#   (Minuet AI provides real-time LLM autocompletion directly inside blink.cmp)
#   -- LSP & Debug:
#   <leader>ca       - Code Action / Roslyn quick fixes
#   <leader>cf       - Code formatting (csharpier / ruff / prettier / rustfmt)
#   <leader>cr       - Rename symbol
#   <leader>dc       - Debug .NET C# application (netcoredbg DAP)
#   <leader>db       - Toggle debugger breakpoint
# Check plugin and LSP status:
#   :Lazy
#   :Mason
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
├── bootstrap.py                 # Main CLI runner (18 tasks pipeline)
├── dotfiles_fallback/           # Bundled fallback dotfiles & Modern Neovim pack
│   ├── .zshrc
│   ├── .zsh_aliases
│   └── .config/
│       ├── kitty/
│       │   ├── kitty.conf
│       │   └── current-theme.conf
│       ├── nvim/                # Modern Lean Neovim Native Pack (Catppuccin, Roslyn, Blink)
│       │   ├── init.lua
│       │   └── lua/
│       │       ├── config/      # options, keymaps, autocmds
│       │       └── plugins/     # ui, editor, lsp, dotnet, completion, treesitter, markdown, etc.
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
│   ├── neovim_dotnet.py         # Modern Lean Neovim pack with Roslyn .NET 10 LSP/DAP
│   ├── ides.py                  # JetBrains Toolbox & native VS Code RPM
│   ├── optional_apps.py         # Antigravity CLI, Zed, Zen, Ollama, LibreOffice, Waydroid, LocalSend
│   ├── dotfiles.py              # GitHub clone OR Fallback symlinking
│   ├── git_onboard.py           # Git defaults onboarding
│   ├── system_tuning.py         # ZRAM memory tuning
│   └── security.py              # SSH server & ed25519 keypair
└── tests/                       # Unit tests & isolated sandbox tests
```
