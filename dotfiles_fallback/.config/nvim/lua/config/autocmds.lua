-- Standard autocommands
local augroup = vim.api.nvim_create_augroup
local autocmd = vim.api.nvim_create_autocmd

-- 1. Highlight on Yank
autocmd("TextYankPost", {
  desc = "Highlight text when yanking",
  group = augroup("highlight-yank", { clear = true }),
  callback = function()
    (vim.hl or vim.highlight).on_yank({ timeout = 150 })
  end,
})

-- 2. Auto-resize splits when window is resized
autocmd("VimResized", {
  desc = "Equalize window splits on resize",
  group = augroup("resize-splits", { clear = true }),
  callback = function()
    local current_tab = vim.fn.tabpagenr()
    vim.cmd("tabdo wincmd =")
    vim.cmd("tabnext " .. current_tab)
  end,
})

-- 3. Filetype specific indentation rules (2 spaces for Web/Lua/Data, 4 spaces for C#/Python/Rust)
autocmd("FileType", {
  desc = "Two-space indentation for web, lua, and config files",
  group = augroup("tab-spacing", { clear = true }),
  pattern = {
    "lua",
    "javascript",
    "typescript",
    "javascriptreact",
    "typescriptreact",
    "html",
    "css",
    "scss",
    "json",
    "yaml",
    "markdown",
  },
  callback = function()
    vim.opt_local.tabstop = 2
    vim.opt_local.shiftwidth = 2
    vim.opt_local.softtabstop = 2
  end,
})

-- 4. Close auxiliary buffers easily with 'q'
autocmd("FileType", {
  desc = "Close documentation and utility buffers with 'q'",
  group = augroup("close-with-q", { clear = true }),
  pattern = {
    "help",
    "lspinfo",
    "man",
    "qf",
    "checkhealth",
    "notify",
  },
  callback = function(event)
    vim.bo[event.buf].buflisted = false
    vim.keymap.set("n", "q", "<cmd>close<cr>", { buffer = event.buf, silent = true, desc = "Close Buffer" })
  end,
})
