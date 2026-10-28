-- Tree-sitter Syntax Highlighting across Polyglot Languages
return {
  {
    "nvim-treesitter/nvim-treesitter",
    build = ":TSUpdate",
    event = { "BufReadPost", "BufNewFile" },
    opts = {
      ensure_installed = {
        -- Requested Polyglot Languages:
        "c_sharp",
        "python",
        "javascript",
        "typescript",
        "tsx",
        "html",
        "css",
        "rust",
        "markdown",
        "markdown_inline",
        -- Data & Configuration:
        "json",
        "yaml",
        "toml",
        "xml",
        "sql",
        -- Shell & Neovim:
        "bash",
        "lua",
        "luadoc",
        "vim",
        "vimdoc",
      },
      highlight = {
        enable = true,
        additional_vim_regex_highlighting = false,
      },
      indent = {
        enable = true,
      },
    },
    config = function(_, opts)
      local ok, ts_configs = pcall(require, "nvim-treesitter.configs")
      if ok then
        ts_configs.setup(opts)
      else
        require("nvim-treesitter.config").setup(opts)
      end
    end,
  },
}
