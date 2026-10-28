-- UI Theme, Statusline, Icons, and Which-Key Help Menu
return {
  -- 1. Catppuccin Mocha Colorscheme (matches Kitty, wallpapers, and Charcoal palette)
  {
    "catppuccin/nvim",
    name = "catppuccin",
    priority = 1000,
    lazy = false,
    opts = {
      flavour = "mocha",
      transparent_background = false,
      integrations = {
        blink_cmp = true,
        fzf = true,
        gitsigns = true,
        native_lsp = {
          enabled = true,
          underlines = {
            errors = { "undercurl" },
            hints = { "undercurl" },
            warnings = { "undercurl" },
            information = { "undercurl" },
          },
        },
        treesitter = true,
        which_key = true,
      },
    },
    config = function(_, opts)
      require("catppuccin").setup(opts)
      vim.cmd.colorscheme("catppuccin")
    end,
  },

  -- 2. Interactive Keybinding Help Popup (shows categorized keybindings)
  {
    "folke/which-key.nvim",
    event = "VeryLazy",
    opts = {
      preset = "modern",
      spec = {
        { "<leader>b", group = "Buffers" },
        { "<leader>c", group = "Code & LSP" },
        { "<leader>d", group = "Debug (DAP)" },
        { "<leader>f", group = "Find & Grep" },
        { "<leader>s", group = "Splits" },
        { "<leader>t", group = "Test" },
        { "<leader>w", group = "Windows / Save" },
        { "<leader>x", group = "Diagnostics" },
      },
    },
    keys = {
      {
        "<leader>?",
        function()
          require("which-key").show({ global = true })
        end,
        desc = "Show All Keybindings Help",
      },
    },
  },

  -- 3. Modern, ultra-lightweight statusline (mini.statusline)
  {
    "echasnovski/mini.statusline",
    version = "*",
    event = "VeryLazy",
    opts = {
      use_icons = true,
    },
    config = function(_, opts)
      require("mini.statusline").setup(opts)
    end,
  },

  -- 4. Lightweight file and filetype icons (mini.icons)
  {
    "echasnovski/mini.icons",
    version = "*",
    lazy = true,
    opts = {},
    init = function()
      package.preload["nvim-web-devicons"] = function()
        require("mini.icons").mock_nvim_web_devicons()
        return package.loaded["nvim-web-devicons"]
      end
    end,
  },
}
