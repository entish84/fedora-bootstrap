#!/usr/bin/env python3
"""
================================================================================
Fedora Linux 44 Post-Installation & Developer Bootstrapper
================================================================================
A modular, idempotent, and interactive system provisioning tool designed for
Fedora Linux 44. Supports Workstation (GNOME) and Minimal (CLI/Niri) profiles.
"""

import argparse
import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.context import ExecutionContext
from core.executor import run_root
from core.logger import logger, ANSIColors
from core.state import StateTracker
from core.ui import (
    print_banner,
    prompt_choice,
    prompt_yes_no,
    prompt_text,
    prompt_checkboxes,
    print_plan_summary,
)
from modules.base import TaskRunner
from modules.dnf_config import DnfConfigTask
from modules.repositories import RepositoriesTask
from modules.multimedia import MultimediaTask
from modules.nvidia import NvidiaTask
from modules.packages import PackagesTask
from modules.dev_tools import DevToolsTask
from modules.desktop_gnome import DesktopGnomeTask
from modules.desktop_dms_niri import DesktopDmsNiriTask
from modules.wallpapers import WallpapersTask
from modules.virtualization import VirtualizationTask
from modules.shell_env import ShellEnvTask
from modules.neovim_dotnet import NeovimDotnetTask
from modules.ides import IdesTask
from modules.dotfiles import DotfilesTask
from modules.git_onboard import GitOnboardTask
from modules.system_tuning import SystemTuningTask
from modules.security import SecurityTask


def check_root_privileges(dry_run: bool = False) -> None:
    """Ensure the script is executed with root/sudo privileges unless dry_run."""
    if os.geteuid() != 0 and not dry_run:
        print(
            f"{ANSIColors.RED}{ANSIColors.BOLD}Error: This script must be run with sudo privileges.{ANSIColors.RESET}\n"
            f"Usage: sudo python3 {sys.argv[0]} [options]\n"
            f"Or test safely in simulation mode: python3 {sys.argv[0]} --dry-run",
            file=sys.stderr,
        )
        sys.exit(1)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fedora Linux 44 Modular Post-Installation Bootstrapper",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--profile",
        choices=["workstation", "minimal"],
        help="System profile: workstation (GNOME) or minimal (CLI / optional Niri)",
    )
    parser.add_argument(
        "--dotfiles",
        type=str,
        help="GitHub dotfiles repository (e.g. username/dotfiles or https://github.com/user/dotfiles.git)",
    )
    parser.add_argument(
        "--with-niri",
        action="store_true",
        help="Install DankLinux Shell with Niri Wayland compositor (for minimal profile)",
    )
    parser.add_argument(
        "--with-nvidia",
        action="store_true",
        help="Install NVIDIA proprietary drivers (akmod-nvidia and CUDA)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate operations without modifying the live system",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Execute immediately using default or argument-provided selections",
    )
    parser.add_argument(
        "--state-file",
        type=Path,
        default=Path("/var/lib/fedora-bootstrap/state.json"),
        help="Path to state tracking journal file",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=Path("/var/log/fedora_bootstrap.log"),
        help="Path to persistent log file",
    )
    return parser.parse_args()


def run_wizard(ctx: ExecutionContext) -> None:
    """Interactive wizard to configure profile, hardware, IDEs, and dotfiles."""
    print_banner()

    # 1. Profile Selection
    profile_options = [
        ("workstation", "Fedora 44 Workstation (GNOME Desktop Environment)"),
        ("minimal", "Fedora 44 Minimal (Base System, CLI/TUI Only, No Heavy DE)"),
    ]
    ctx.profile = prompt_choice(
        "Select your target installation profile:",
        profile_options,
        default_idx=0 if ctx.profile == "workstation" else 1,
    )

    # 2. Graphics & Codecs
    print(
        f"\n{ANSIColors.GREEN}✔ AMD GPU Hardware Acceleration (Mesa Freeworld VA-API/VDPAU) is MANDATORY and enabled.{ANSIColors.RESET}"
    )
    ctx.enable_nvidia = prompt_yes_no(
        "Do you have an NVIDIA GPU and want to install akmod-nvidia proprietary drivers?",
        default=False,
    )

    # 3. Minimal Profile Desktop Option
    if ctx.profile == "minimal":
        ctx.enable_dms_niri = prompt_yes_no(
            "Do you want to install DankLinux Shell with Niri (DMS + Niri Wayland Compositor)?",
            default=True,
        )

    # 4. Workstation Productivity
    if ctx.profile == "workstation":
        ctx.enable_gnome_productivity = prompt_yes_no(
            "Enable GNOME Productivity Suite (AppIndicator tray icons, Dash-to-Dock, Blur-My-Shell, window controls)?",
            default=True,
        )

    # 5. IDE & Editor Selection (Native Only)
    ide_options = [
        ("jetbrains_toolbox", "JetBrains Toolbox (Native /opt - manages Rider, Android Studio, CLion)", True),
        ("vscode", "Visual Studio Code (Native RPM from Microsoft)", True),
        ("neovim", "Neovim with LazyVim & .NET 10 Ready (OmniSharp/Roslyn LSP, DAP, CSharpier)", True),
    ]
    ctx.selected_ides = prompt_checkboxes(
        "Select development environments and editors to install (Native RPMs only, no Flatpaks):",
        ide_options,
    )

    # 6. Developer TUI Suite
    ctx.install_dev_tools = prompt_yes_no(
        "Install Developer TUI Tools (lazygit, lazydocker, jujutsu, uv, tealdeer, duf, procs)?",
        default=True,
    )

    # 7. Minimal Wallpapers
    ctx.enable_wallpapers = prompt_yes_no(
        "Download Catppuccin Minimal Wallpapers from GitHub and configure desktop background?",
        default=True,
    )

    # 8. Dotfiles Configuration
    repo_input = prompt_text(
        "Enter your GitHub dotfiles repository (e.g. username/dotfiles) or press Enter to use bundled fallback",
        default="",
    )
    if repo_input:
        ctx.dotfiles_repo = repo_input
        ctx.use_fallback_dotfiles = False
    else:
        ctx.dotfiles_repo = None
        ctx.use_fallback_dotfiles = True
        print(
            f"{ANSIColors.CYAN}ℹ Using bundled Charcoal-Amber fallback suite (.zshrc, .zsh_aliases, kitty, starship).{ANSIColors.RESET}"
        )


def main() -> None:
    args = parse_arguments()
    check_root_privileges(dry_run=args.dry_run)

    # Initialize execution context
    ctx = ExecutionContext.detect(dry_run=args.dry_run)
    ctx.state_file = args.state_file
    if args.log_file:
        ctx.log_file = args.log_file
    actual_log = logger.set_log_file(ctx.log_file)
    ctx.log_file = actual_log
    if args.profile:
        ctx.profile = args.profile
    if args.dotfiles:
        ctx.dotfiles_repo = args.dotfiles
        ctx.use_fallback_dotfiles = False
    if args.with_niri:
        ctx.enable_dms_niri = True
    if args.with_nvidia:
        ctx.enable_nvidia = True

    # Run interactive wizard if not non-interactive
    if not args.non_interactive:
        run_wizard(ctx)

    # Display plan summary
    dotfiles_desc = (
        f"https://github.com/{ctx.dotfiles_repo}"
        if ctx.dotfiles_repo
        else "Bundled Charcoal-Amber Fallback Suite"
    )
    summary = [
        ("Target Profile", "Workstation (GNOME)" if ctx.profile == "workstation" else "Minimal Base"),
        ("Target User", f"{ctx.target_user} (UID: {ctx.target_uid}, Home: {ctx.target_home})"),
        ("Package Strategy", "Terra-First + RPM Fusion + MS + Docker"),
        ("AMD Codecs", "MANDATORY (Mesa Freeworld + FFmpeg Full)"),
        ("NVIDIA Drivers", "Enabled" if ctx.enable_nvidia else "Disabled"),
        ("Wayland Compositor", "DankLinux Shell + Niri" if ctx.enable_dms_niri else "Default GNOME / TTY"),
        ("Selected IDEs", ", ".join(ctx.selected_ides) if ctx.selected_ides else "None"),
        ("Developer TUIs", "lazygit, lazydocker, jj, uv, tealdeer" if ctx.install_dev_tools else "Skipped"),
        ("Dotfiles Source", dotfiles_desc),
        ("Wallpapers", "Catppuccin Minimalist Pack" if ctx.enable_wallpapers else "Skipped"),
        ("Log File", str(ctx.log_file)),
        ("State Journal", str(ctx.state_file)),
        ("Execution Mode", "DRY-RUN SIMULATION" if ctx.dry_run else "LIVE EXECUTION"),
    ]
    print_plan_summary(summary)

    if not args.non_interactive:
        proceed = prompt_yes_no("Proceed with pipeline execution?", default=True)
        if not proceed:
            print(f"{ANSIColors.YELLOW}Execution aborted by user.{ANSIColors.RESET}")
            sys.exit(0)

    # Initialize State Tracker and Task Runner
    state = StateTracker(ctx)
    runner = TaskRunner(ctx, state)

    # Register Tasks in strict sequential order
    runner.register(DnfConfigTask())
    runner.register(RepositoriesTask())
    runner.register(MultimediaTask())
    runner.register(NvidiaTask())
    runner.register(PackagesTask())
    runner.register(DevToolsTask())
    runner.register(DesktopGnomeTask())
    runner.register(DesktopDmsNiriTask())
    runner.register(WallpapersTask())
    runner.register(VirtualizationTask())
    runner.register(ShellEnvTask())
    runner.register(NeovimDotnetTask())
    runner.register(IdesTask())
    runner.register(DotfilesTask())
    runner.register(GitOnboardTask())
    runner.register(SystemTuningTask())
    runner.register(SecurityTask())

    # Execute all tasks
    success = runner.run_all()

    if success:
        print(f"\n{ANSIColors.GREEN}{ANSIColors.BOLD}================================================================================")
        print("                 BOOTSTRAP COMPLETED SUCCESSFULLY!")
        print(f"================================================================================{ANSIColors.RESET}\n")

        if not ctx.dry_run:
            reboot_now = prompt_yes_no("It is recommended to reboot your system. Reboot now?", default=False)
            if reboot_now:
                logger.info("Initiating system reboot...")
                run_root("reboot", ctx, check=False)
    else:
        print(f"\n{ANSIColors.RED}{ANSIColors.BOLD}Bootstrap finished with errors. Check /var/log/fedora_bootstrap.log for details.{ANSIColors.RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
