"""Neovim with LazyVim and out-of-the-box .NET 10 development toolchain."""

from pathlib import Path
from core.context import ExecutionContext
from core.executor import run_root, run_user
from core.logger import logger
from modules.base import BaseTask


class NeovimDotnetTask(BaseTask):
    name = "neovim_dotnet"
    description = "Bootstrap Neovim with LazyVim and complete .NET 10 C# coding environment"

    DOTNET_PLUGIN_LUA = """-- Full out-of-the-box C# / .NET 10 development configuration for LazyVim
return {
  -- 1. Treesitter syntax highlighting for C#
  {
    "nvim-treesitter/nvim-treesitter",
    opts = function(_, opts)
      if type(opts.ensure_installed) == "table" then
        vim.list_extend(opts.ensure_installed, { "c_sharp" })
      end
    end,
  },

  -- 2. Mason tool installer: ensure Omnisharp, CSharpier, and NetCoreDbg are ready
  {
    "williamboman/mason.nvim",
    opts = function(_, opts)
      opts.ensure_installed = opts.ensure_installed or {}
      vim.list_extend(opts.ensure_installed, {
        "omnisharp",
        "csharpier",
        "netcoredbg",
      })
    end,
  },

  -- 3. LSP Configuration: Omnisharp with modern .NET 10 SDK support
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        omnisharp = {
          enable_roslyn_analyzers = true,
          enable_import_completion = true,
          organize_imports_on_format = true,
          enable_decompilation_support = true,
        },
      },
    },
  },

  -- 4. Code Formatter: CSharpier
  {
    "stevearc/conform.nvim",
    optional = true,
    opts = {
      formatters_by_ft = {
        cs = { "csharpier" },
      },
    },
  },

  -- 5. DAP Debugger: netcoredbg integration
  {
    "mfussenegger/nvim-dap",
    optional = true,
    opts = function()
      local dap = require("dap")
      dap.adapters.coreclr = {
        type = "executable",
        command = "netcoredbg",
        args = { "--interpreter=vscode" },
      }
      dap.configurations.cs = {
        {
          type = "coreclr",
          name = "launch - netcoredbg",
          request = "launch",
          program = function()
            return vim.fn.input("Path to dll: ", vim.fn.getcwd() .. "/bin/Debug/", "file")
          end,
        },
      }
    end,
  },

  -- 6. Testing: neotest-dotnet
  {
    "nvim-neotest/neotest",
    optional = true,
    dependencies = {
      "Issafalcon/neotest-dotnet",
    },
    opts = {
      adapters = {
        ["neotest-dotnet"] = {},
      },
    },
  },
}
"""

    def is_applicable(self, ctx: ExecutionContext) -> bool:
        return "neovim" in ctx.selected_ides

    def check(self, ctx: ExecutionContext) -> bool:
        dotnet_plugin = ctx.target_home / ".config" / "nvim" / "lua" / "plugins" / "dotnet.lua"
        return dotnet_plugin.exists()

    def apply(self, ctx: ExecutionContext) -> bool:
        logger.info("Installing Neovim from Terra/Fedora...")
        run_root("dnf install -y neovim", ctx, check=False)

        nvim_dir = ctx.target_home / ".config" / "nvim"
        lazy_lua = nvim_dir / "lua" / "config" / "lazy.lua"

        # Clone LazyVim starter if not already present
        if not lazy_lua.exists():
            logger.info("Cloning LazyVim starter template...")
            cmd = f"git clone https://github.com/LazyVim/starter '{nvim_dir}' || true"
            run_user(cmd, ctx, check=False)
            run_user(f"rm -rf '{nvim_dir}/.git'", ctx, check=False)

        # Write .NET 10 plugin configuration
        plugins_dir = nvim_dir / "lua" / "plugins"
        dotnet_plugin = plugins_dir / "dotnet.lua"
        logger.info("Writing .NET 10 LSP/DAP/CSharpier configuration to Neovim...")
        if not ctx.dry_run:
            plugins_dir.mkdir(parents=True, exist_ok=True)
            dotnet_plugin.write_text(self.DOTNET_PLUGIN_LUA, encoding="utf-8")

        # Fix ownership
        run_user(f"chown -R {ctx.target_user}:{ctx.target_user} '{nvim_dir}'", ctx, check=False)
        return True
