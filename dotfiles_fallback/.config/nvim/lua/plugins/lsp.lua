-- Language Server Protocol (LSP) Configuration & Mason Tool Installer
return {
  -- 1. Mason package manager for language servers, formatters, and debuggers
  {
    "williamboman/mason.nvim",
    cmd = "Mason",
    build = ":MasonUpdate",
    opts = {
      registries = {
        "github:mason-org/mason-registry",
        "github:Crashdummyy/mason-registry", -- Provides official Microsoft Roslyn LSP
      },
      ui = {
        border = "rounded",
        icons = {
          package_installed = "✓",
          package_pending = "➜",
          package_uninstalled = "✗",
        },
      },
    },
  },

  -- 2. Mason bridge to nvim-lspconfig & Native Neovim 0.12 LSP
  {
    "williamboman/mason-lspconfig.nvim",
    dependencies = {
      "williamboman/mason.nvim",
      "neovim/nvim-lspconfig",
      "Saghen/blink.cmp",
    },
    opts = {
      ensure_installed = {
        "pyright",        -- Python
        "ts_ls",          -- JavaScript / TypeScript
        "html",           -- HTML
        "cssls",          -- CSS
        "rust_analyzer",  -- Rust
        "marksman",       -- Markdown
        "lua_ls",         -- Lua / Neovim config
      },
      automatic_installation = true,
    },
    config = function(_, opts)
      local mason_lspconfig = require("mason-lspconfig")
      local blink = require("blink.cmp")

      mason_lspconfig.setup(opts)

      -- Broadcast Blink.cmp capabilities to all LSP servers
      local capabilities = blink.get_lsp_capabilities()

      -- Global LspAttach keybindings
      vim.api.nvim_create_autocmd("LspAttach", {
        desc = "LSP Keybindings on Buffer Attach",
        callback = function(args)
          local bufnr = args.buf
          local function nmap(keys, func, desc)
            vim.keymap.set("n", keys, func, { buffer = bufnr, desc = desc })
          end

          nmap("gd", vim.lsp.buf.definition, "Go to Definition")
          nmap("gr", vim.lsp.buf.references, "Find References")
          nmap("gi", vim.lsp.buf.implementation, "Go to Implementation")
          nmap("gy", vim.lsp.buf.type_definition, "Type Definition")
          nmap("K", vim.lsp.buf.hover, "Hover Documentation")
          nmap("<leader>ca", vim.lsp.buf.code_action, "Code Action")
          nmap("<leader>cr", vim.lsp.buf.rename, "Rename Symbol")

          -- Inlay hints toggle (Neovim 0.10+ native)
          local client = vim.lsp.get_client_by_id(args.data.client_id)
          if client and client.server_capabilities.inlayHintProvider then
            vim.lsp.inlay_hint.enable(true, { bufnr = bufnr })
          end
        end,
      })

      -- Supported polyglot language servers configured natively via Neovim 0.12 vim.lsp.config
      local servers = {
        "pyright",
        "ts_ls",
        "html",
        "cssls",
        "rust_analyzer",
        "marksman",
        "lua_ls",
      }

      for _, server_name in ipairs(servers) do
        local server_opts = {
          capabilities = capabilities,
        }

        if server_name == "lua_ls" then
          server_opts.settings = {
            Lua = {
              workspace = { checkThirdParty = false },
              telemetry = { enable = false },
              diagnostics = { globals = { "vim" } },
            },
          }
        elseif server_name == "pyright" then
          server_opts.settings = {
            python = {
              analysis = {
                autoSearchPaths = true,
                useLibraryCodeForTypes = true,
                diagnosticMode = "workspace",
              },
            },
          }
        end

        vim.lsp.config[server_name] = server_opts
        vim.lsp.enable(server_name)
      end
    end,
  },
}
