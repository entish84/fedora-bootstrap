-- Terminal Integration, Live Web Server & Polyglot Run/Build Workflows
return {
  {
    "akinsho/toggleterm.nvim",
    version = "*",
    keys = {
      { [[<C-\>]], desc = "Toggle Terminal" },
      { "<leader>tt", "<cmd>ToggleTerm direction=float<cr>", desc = "Terminal (Floating)" },
      { "<leader>th", "<cmd>ToggleTerm size=15 direction=horizontal<cr>", desc = "Terminal (Horizontal)" },
      { "<leader>tv", "<cmd>ToggleTerm size=80 direction=vertical<cr>", desc = "Terminal (Vertical)" },
      -- .NET
      { "<leader>rr", desc = "dotnet run (Interactive)" },
      { "<leader>rw", desc = "dotnet watch run (Hot Reload)" },
      { "<leader>rb", desc = "dotnet build (Terminal)" },
      { "<leader>rB", desc = "dotnet build (Quickfix List)" },
      { "<leader>rt", desc = "dotnet test (Terminal)" },
      { "<leader>rc", desc = "dotnet clean" },
      -- Python Web
      { "<leader>ru", desc = "FastAPI / Uvicorn (uv run uvicorn --reload)" },
      { "<leader>rf", desc = "Flask (uv run flask run --debug)" },
      { "<leader>rd", desc = "Django (uv run python manage.py runserver)" },
      -- Web Development (Live Server)
      { "<leader>ws", desc = "Start Live Server (Zen Browser)" },
      { "<leader>wS", desc = "Stop Live Server" },
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

      -- 1. Dedicated persistent terminals for .NET workflows
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

      -- 2. Dedicated Python Web Runners (FastAPI, Flask, Django via uv)
      local uvicorn_server = Terminal:new({
        cmd = "uv run uvicorn main:app --reload --port 8000",
        direction = "horizontal",
        size = 14,
        close_on_exit = false,
        hidden = true,
      })

      local flask_server = Terminal:new({
        cmd = "uv run flask run --debug",
        direction = "horizontal",
        size = 14,
        close_on_exit = false,
        hidden = true,
      })

      local django_server = Terminal:new({
        cmd = "uv run python manage.py runserver",
        direction = "horizontal",
        size = 14,
        close_on_exit = false,
        hidden = true,
      })

      vim.keymap.set("n", "<leader>ru", function()
        uvicorn_server:toggle()
      end, { desc = "FastAPI: Uvicorn Server (--reload)" })

      vim.keymap.set("n", "<leader>rf", function()
        flask_server:toggle()
      end, { desc = "Flask: Dev Server (--debug)" })

      vim.keymap.set("n", "<leader>rd", function()
        django_server:toggle()
      end, { desc = "Django: Run Server" })

      -- 3. Dedicated Live Server for HTML/CSS/JS (auto-opens Zen Browser)
      local live_server = nil

      vim.keymap.set("n", "<leader>ws", function()
        if not live_server then
          live_server = Terminal:new({
            cmd = "live-server --port=5500 --browser=zen-browser",
            direction = "horizontal",
            size = 12,
            close_on_exit = false,
            hidden = true,
          })
        end
        live_server:open()
        vim.notify("Live Server started at http://127.0.0.1:5500 (Zen Browser)", vim.log.levels.INFO)
      end, { desc = "Start Live Server (Zen Browser)" })

      vim.keymap.set("n", "<leader>wS", function()
        if live_server then
          live_server:shutdown()
          live_server = nil
          vim.notify("Live Server stopped.", vim.log.levels.INFO)
        else
          vim.notify("Live Server is not running.", vim.log.levels.WARN)
        end
      end, { desc = "Stop Live Server" })

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
