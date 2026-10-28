-- C# / .NET 10 Toolchain (Official Microsoft Roslyn LSP, NetCoreDbg DAP, Neotest)
return {
  -- 1. Official Microsoft Roslyn Language Server (seblyng/roslyn.nvim)
  {
    "seblyng/roslyn.nvim",
    ft = { "cs", "razor" },
    opts = {
      filewatching = "roslyn",
    },
    config = function(_, opts)
      require("roslyn").setup(opts)

      -- Configure Roslyn compiler-backed inlay hints and solution diagnostics
      vim.lsp.config("roslyn", {
        settings = {
          ["csharp|inlay_hints"] = {
            csharp_enable_inlay_hints_for_implicit_object_creation = true,
            csharp_enable_inlay_hints_for_implicit_variable_types = true,
            csharp_enable_inlay_hints_for_lambda_parameter_types = true,
            csharp_enable_inlay_hints_for_types = true,
            dotnet_show_completion_items_from_unimported_namespaces = true,
            dotnet_show_name_completion_suggestions = true,
          },
          ["csharp|background_analysis"] = {
            dotnet_compiler_diagnostics_scope = "fullSolution",
            dotnet_analyzer_diagnostics_scope = "fullSolution",
          },
        },
      })
      vim.lsp.enable("roslyn")
    end,
  },

  -- 2. Debug Adapter Protocol (DAP) for .NET via NetCoreDbg
  {
    "mfussenegger/nvim-dap",
    keys = {
      { "<leader>db", function() require("dap").toggle_breakpoint() end, desc = "Toggle Breakpoint" },
      { "<leader>dc", function() require("dap").continue() end, desc = "Debug: Continue / Start" },
      { "<leader>di", function() require("dap").step_into() end, desc = "Debug: Step Into" },
      { "<leader>do", function() require("dap").step_over() end, desc = "Debug: Step Over" },
      { "<leader>dO", function() require("dap").step_out() end, desc = "Debug: Step Out" },
      { "<leader>dt", function() require("dap").terminate() end, desc = "Debug: Terminate" },
    },
    config = function()
      local dap = require("dap")
      dap.adapters.coreclr = {
        type = "executable",
        command = "netcoredbg",
        args = { "--interpreter=vscode" },
      }
      dap.configurations.cs = {
        {
          type = "coreclr",
          name = "Launch .NET App (netcoredbg)",
          request = "launch",
          program = function()
            return vim.fn.input("Path to target DLL: ", vim.fn.getcwd() .. "/bin/Debug/", "file")
          end,
        },
      }
    end,
  },

  -- 3. Unit Testing Runner: neotest with neotest-dotnet & neotest-python
  {
    "nvim-neotest/neotest",
    dependencies = {
      "nvim-neotest/nvim-nio",
      "nvim-lua/plenary.nvim",
      "nvim-treesitter/nvim-treesitter",
      "Issafalcon/neotest-dotnet",
      "nvim-neotest/neotest-python",
    },
    keys = {
      { "<leader>tr", function() require("neotest").run.run() end, desc = "Run Nearest Test" },
      { "<leader>tf", function() require("neotest").run.run(vim.fn.expand("%")) end, desc = "Run Test File" },
      { "<leader>ts", function() require("neotest").summary.toggle() end, desc = "Toggle Test Summary" },
      { "<leader>tp", function() require("neotest").run.run({ suite = true }) end, desc = "Run Test Suite (Pytest / .NET)" },
    },
    opts = function()
      local adapters = {
        require("neotest-dotnet")({
          dap = { args = { "--interpreter=vscode" } },
        }),
      }
      local ok, neotest_python = pcall(require, "neotest-python")
      if ok then
        table.insert(adapters, neotest_python({ runner = "pytest" }))
      end
      return {
        adapters = adapters,
      }
    end,
  },
}
