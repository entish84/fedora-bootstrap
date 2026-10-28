-- Editor options & behaviors
local opt = vim.opt

-- Line numbers: Relative line numbers for fast vertical motions (e.g. 10j, 5k)
opt.number = true
opt.relativenumber = true

-- Indentation & Tabs (defaults to 4 spaces; filetype autocmds override for web/lua)
opt.tabstop = 4
opt.shiftwidth = 4
opt.softtabstop = 4
opt.expandtab = true
opt.smartindent = true
opt.autoindent = true

-- Search configuration
opt.ignorecase = true
opt.smartcase = true
opt.hlsearch = true
opt.incsearch = true

-- Appearance & Display
opt.termguicolors = true
opt.cursorline = true
opt.signcolumn = "yes"
opt.scrolloff = 8
opt.sidescrolloff = 8
opt.wrap = false
opt.showmode = false -- Statusline already shows mode

-- Window split directions
opt.splitbelow = true
opt.splitright = true

-- Clipboard & Persistent History
opt.clipboard = "unnamedplus" -- Wayland wl-copy & X11 clipboard integration
opt.undofile = true
opt.undolevels = 10000
opt.swapfile = false
opt.backup = false

-- Performance & Ergonomics
opt.updatetime = 200
opt.timeoutlen = 300 -- Fast which-key popup trigger (300ms)
opt.completeopt = "menu,menuone,noselect"
opt.mouse = "a"
opt.confirm = true -- Confirm to save changes before exiting modified buffer
