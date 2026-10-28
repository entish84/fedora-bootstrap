-- Fuzzy Finder (fzf-lua), File Explorer (mini.files), and Git (gitsigns)
return {
  -- 1. Blazing fast fuzzy finding via native fzf binary
  {
    "ibhagwan/fzf-lua",
    cmd = "FzfLua",
    keys = {
      { "<leader>ff", "<cmd>FzfLua files<cr>", desc = "Find Files" },
      { "<leader>fg", "<cmd>FzfLua live_grep<cr>", desc = "Live Grep (Text)" },
      { "<leader>fb", "<cmd>FzfLua buffers<cr>", desc = "Find Buffers" },
      { "<leader>fr", "<cmd>FzfLua oldfiles<cr>", desc = "Recent Files" },
      { "<leader>fk", "<cmd>FzfLua keymaps<cr>", desc = "Find Keymaps" },
      { "<leader>fs", "<cmd>FzfLua lsp_document_symbols<cr>", desc = "Document Symbols" },
      { "<leader>gs", "<cmd>FzfLua git_status<cr>", desc = "Git Status" },
    },
    opts = {
      winopts = {
        height = 0.85,
        width = 0.85,
        preview = {
          layout = "flex",
        },
      },
      keymap = {
        builtin = {
          ["<C-d>"] = "preview-page-down",
          ["<C-u>"] = "preview-page-up",
        },
      },
    },
  },

  -- 2. Fast columnar file manager & directory explorer
  {
    "echasnovski/mini.files",
    version = "*",
    keys = {
      {
        "<leader>e",
        function()
          local mf = require("mini.files")
          if not mf.close() then
            mf.open(vim.api.nvim_buf_get_name(0), true)
          end
        end,
        desc = "Toggle File Explorer",
      },
    },
    opts = {
      windows = {
        preview = true,
        width_focus = 30,
        width_preview = 45,
      },
      options = {
        use_as_default_explorer = true,
      },
    },
  },

  -- 3. Git status signs and hunk actions in the sign column
  {
    "lewis6991/gitsigns.nvim",
    event = { "BufReadPre", "BufNewFile" },
    opts = {
      signs = {
        add = { text = "▎" },
        change = { text = "▎" },
        delete = { text = "" },
        topdelete = { text = "" },
        changedelete = { text = "▎" },
        untracked = { text = "▎" },
      },
      on_attach = function(bufnr)
        local gs = package.loaded.gitsigns

        local function map(mode, l, r, opts)
          opts = opts or {}
          opts.buffer = bufnr
          vim.keymap.set(mode, l, r, opts)
        end

        -- Navigation between Git hunks
        map("n", "]h", function()
          if vim.wo.diff then return "]h" end
          vim.schedule(function() gs.next_hunk() end)
          return "<Ignore>"
        end, { expr = true, desc = "Next Git Hunk" })

        map("n", "[h", function()
          if vim.wo.diff then return "[h" end
          vim.schedule(function() gs.prev_hunk() end)
          return "<Ignore>"
        end, { expr = true, desc = "Prev Git Hunk" })

        map("n", "<leader>hp", gs.preview_hunk, { desc = "Preview Hunk Diff" })
        map("n", "<leader>hb", function() gs.blame_line({ full = true }) end, { desc = "Blame Line" })
      end,
    },
  },
}
