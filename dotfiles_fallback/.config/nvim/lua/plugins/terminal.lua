-- Terminal Integration & Modern .NET Run / Build Workflows
return {
  {
    "akinsho/toggleterm.nvim",
    version = "*",
    keys = {
      { [[<C-\>]], desc = "Toggle Terminal" },
      { "<leader>tt", "<cmd>ToggleTerm direction=float<cr>", desc = "Terminal (Floating)" },
      { "<leader>th", "<cmd>ToggleTerm size=15 direction=horizontal<cr>", desc = "Terminal (Horizontal)" },
      { "<leader>tv", "<cmd>ToggleTerm size=80 direction=vertical<cr>", desc = "Terminal (Vertical)" },
      { "<leader>rr", desc = "dotnet run (Interactive)" },
      { "<leader>rw", desc = "dotnet watch run (Hot Reload)" },
      { "<leader>rb", desc = "dotnet build (Terminal)" },
      { "<leader>rB", desc = "dotnet build (Quickfix List)" },
      { "<leader>rt", desc = "dotnet test (Terminal)" },
      { "<leader>rc", desc = "dotnet clean" },
    },
    opts = {
      open_mapping = [[<C-\>]],
      hide_numbers = true,
      shade_terminals = false,
      start_in_insert = true,
      insert_mappings = true,
      terminal_mappings = true,
      persist_size = true,
      direction = "float",
      close_on_exit = false,
      float_opts = {
        border = "rounded",
        winblend = 0,
      },
      size = function(term)
        if term.direction == "horizontal" then
          return 15
        elseif term.direction == "vertical" then
          return vim.o.columns * 0.4
        end
      end,
    },
    config = function(_, opts)
      require("toggleterm").setup(opts)

      local Terminal = require("toggleterm.terminal").Terminal

      -- Dedicated persistent terminals for .NET workflows
      local dotnet_run = Terminal:new({
        cmd = "dotnet run",
        direction = "float",
        close_on_exit = false,
        hidden = true,
        on_open = function(_)
          vim.cmd("startinsert!")
        end,
      })

      local dotnet_watch = Terminal:new({
        cmd = "dotnet watch run",
        direction = "horizontal",
        size = 15,
        close_on_exit = false,
        hidden = true,
        on_open = function(_)
          vim.cmd("startinsert!")
        end,
      })

      local dotnet_build = Terminal:new({
        cmd = "dotnet build",
        direction = "float",
        close_on_exit = false,
        hidden = true,
      })

      local dotnet_test = Terminal:new({
        cmd = "dotnet test",
        direction = "float",
        close_on_exit = false,
        hidden = true,
      })

      local dotnet_clean = Terminal:new({
        cmd = "dotnet clean",
        direction = "float",
        close_on_exit = false,
        hidden = true,
      })

      -- Keybindings for Run & Build (.NET)
      vim.keymap.set("n", "<leader>rr", function()
        dotnet_run:toggle()
      end, { desc = "dotnet run (Interactive)" })

      vim.keymap.set("n", "<leader>rw", function()
        dotnet_watch:toggle()
      end, { desc = "dotnet watch run (Hot Reload)" })

      vim.keymap.set("n", "<leader>rb", function()
        dotnet_build:toggle()
      end, { desc = "dotnet build (Terminal)" })

      vim.keymap.set("n", "<leader>rt", function()
        dotnet_test:toggle()
      end, { desc = "dotnet test (Terminal)" })

      vim.keymap.set("n", "<leader>rc", function()
        dotnet_clean:toggle()
      end, { desc = "dotnet clean" })

      -- Quickfix build using native Neovim compiler (compiler dotnet)
      vim.keymap.set("n", "<leader>rB", function()
        vim.cmd("compiler dotnet")
        vim.cmd("make")
        vim.cmd("copen")
      end, { desc = "dotnet build (Quickfix List)" })

      -- Convenient terminal navigation & exit
      function _G.set_terminal_keymaps()
        local t_opts = { buffer = 0 }
        vim.keymap.set("t", "<C-x>", [[<C-\><C-n>]], t_opts)
        vim.keymap.set("t", "<C-h>", [[<Cmd>wincmd h<CR>]], t_opts)
        vim.keymap.set("t", "<C-j>", [[<Cmd>wincmd j<CR>]], t_opts)
        vim.keymap.set("t", "<C-k>", [[<Cmd>wincmd k<CR>]], t_opts)
        vim.keymap.set("t", "<C-l>", [[<Cmd>wincmd l<CR>]], t_opts)
      end

      vim.api.nvim_create_autocmd("TermOpen", {
        pattern = "term://*",
        callback = function()
          _G.set_terminal_keymaps()
        end,
      })
    end,
  },
}
