-- HTML, CSS, JavaScript Live Web Development Suite
return {
  -- 1. Emmet Abbreviation Expansion for HTML / CSS / JSX
  {
    "olrtg/nvim-emmet",
    ft = { "html", "css", "javascriptreact", "typescriptreact", "vue", "svelte" },
    config = function()
      vim.keymap.set({ "n", "v" }, "<leader>we", require("nvim-emmet").wrap_with_abbreviation, { desc = "Emmet: Wrap with Abbreviation" })
    end,
  },
}
