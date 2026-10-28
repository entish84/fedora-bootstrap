-- Python Modern Web Development Suite (FastAPI, Flask, Django, venv-selector)
return {
  -- 1. Automatic Python Virtual Environment Selector
  {
    "linux-cultist/venv-selector.nvim",
    dependencies = {
      "neovim/nvim-lspconfig",
      "ibhagwan/fzf-lua",
    },
    ft = "python",
    keys = {
      { "<leader>cv", "<cmd>VenvSelect<cr>", desc = "Select Python VirtualEnv" },
    },
    opts = {
      settings = {
        options = {
          notify_user_on_venv_activation = true,
        },
      },
    },
  },
}
