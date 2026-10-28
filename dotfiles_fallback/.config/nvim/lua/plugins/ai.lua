-- Antigravity CLI (agy) AI Pair Programming Integration
return {
  {
    "akinsho/toggleterm.nvim",
    optional = true,
  },
  {
    "folke/which-key.nvim",
    optional = true,
  },
  {
    -- Virtual plugin specification to configure AGY actions
    dir = vim.fn.stdpath("config"),
    name = "antigravity-ai",
    keys = {
      { "<leader>aa", desc = "Open Antigravity AI Agent (Floating)" },
      { "<leader>ar", desc = "AGY Code Review (Security & Bugs)", mode = { "n", "v" } },
      { "<leader>ae", desc = "AGY Explain Code", mode = { "n", "v" } },
      { "<leader>af", desc = "AGY Fix / Refactor Code", mode = { "n", "v" } },
      { "<leader>ag", desc = "AGY Generate Unit Tests", mode = { "n", "v" } },
    },
    config = function()
      local Terminal = require("toggleterm.terminal").Terminal

      -- 1. Floating Antigravity CLI Agent Window
      local agy_terminal = Terminal:new({
        cmd = "agy",
        direction = "float",
        close_on_exit = false,
        hidden = true,
        float_opts = {
          border = "curved",
          width = function()
            return math.floor(vim.o.columns * 0.88)
          end,
          height = function()
            return math.floor(vim.o.lines * 0.88)
          end,
        },
      })

      vim.keymap.set({ "n", "v" }, "<leader>aa", function()
        agy_terminal:toggle()
      end, { desc = "Toggle Antigravity AI Agent" })

      -- 2. Helper to display markdown output in floating scratchpad
      local function show_markdown_float(title, content)
        local buf = vim.api.nvim_create_buf(false, true)
        vim.bo[buf].filetype = "markdown"
        local lines = vim.split(content, "\n", { plain = true })
        vim.api.nvim_buf_set_lines(buf, 0, -1, false, lines)
        vim.bo[buf].modifiable = false
        vim.bo[buf].buftype = "nofile"

        local width = math.min(math.floor(vim.o.columns * 0.82), 120)
        local height = math.min(math.floor(vim.o.lines * 0.82), #lines + 4)
        local row = math.floor((vim.o.lines - height) / 2)
        local col = math.floor((vim.o.columns - width) / 2)

        local win = vim.api.nvim_open_win(buf, true, {
          relative = "editor",
          width = width,
          height = height,
          row = row,
          col = col,
          style = "minimal",
          border = "rounded",
          title = " " .. title .. " (Press 'q' to close) ",
          title_pos = "center",
        })

        vim.keymap.set("n", "q", function()
          if vim.api.nvim_win_is_valid(win) then
            vim.api.nvim_win_close(win, true)
          end
        end, { buffer = buf, silent = true, desc = "Close Float" })
      end

      -- 3. Extract text from visual selection or whole buffer
      local function get_code_context(is_visual)
        if is_visual then
          local start_pos = vim.fn.getpos("'<")
          local end_pos = vim.fn.getpos("'>")
          local start_line = start_pos[2] - 1
          local end_line = end_pos[2]
          local lines = vim.api.nvim_buf_get_lines(0, start_line, end_line, false)
          return table.concat(lines, "\n")
        else
          local lines = vim.api.nvim_buf_get_lines(0, 0, -1, false)
          return table.concat(lines, "\n")
        end
      end

      -- 4. Dispatch prompt to `agy -p`
      local function run_agy_prompt(action_name, instruction, is_visual)
        local code = get_code_context(is_visual)
        if not code or code:match("^%s*$") then
          vim.notify("AGY: No code selected to analyze.", vim.log.levels.WARN)
          return
        end

        local ft = vim.bo.filetype
        local prompt = string.format("%s for the following %s code:\n\n```%s\n%s\n```", instruction, ft, ft, code)

        vim.notify("Antigravity AI is thinking (" .. action_name .. ")...", vim.log.levels.INFO)

        vim.system({ "agy", "-p", prompt }, { text = true }, function(obj)
          vim.schedule(function()
            if obj.code == 0 then
              show_markdown_float("Antigravity AI: " .. action_name, obj.stdout)
            else
              vim.notify("AGY Error: " .. (obj.stderr ~= "" and obj.stderr or "Command failed"), vim.log.levels.ERROR)
            end
          end)
        end)
      end

      -- Keybindings for AGY Buffer Actions
      vim.keymap.set("n", "<leader>ar", function()
        run_agy_prompt("Code Review", "Review this code thoroughly for bugs, edge cases, security issues, and performance optimizations", false)
      end, { desc = "AGY Code Review (Buffer)" })

      vim.keymap.set("v", "<leader>ar", function()
        run_agy_prompt("Code Review", "Review this selected code for bugs, edge cases, and performance optimizations", true)
      end, { desc = "AGY Code Review (Selection)" })

      vim.keymap.set("n", "<leader>ae", function()
        run_agy_prompt("Explain Code", "Explain how this code works in detail, including functions, types, and execution flow", false)
      end, { desc = "AGY Explain Code (Buffer)" })

      vim.keymap.set("v", "<leader>ae", function()
        run_agy_prompt("Explain Code", "Explain how this selected code works in detail", true)
      end, { desc = "AGY Explain Code (Selection)" })

      vim.keymap.set("n", "<leader>af", function()
        run_agy_prompt("Refactor & Fix", "Suggest idiomatic refactoring and improvements for this code, providing diffs and explanations", false)
      end, { desc = "AGY Fix / Refactor (Buffer)" })

      vim.keymap.set("v", "<leader>af", function()
        run_agy_prompt("Refactor & Fix", "Suggest idiomatic refactoring and improvements for this code, providing diffs and explanations", true)
      end, { desc = "AGY Fix / Refactor (Selection)" })

      vim.keymap.set("n", "<leader>ag", function()
        run_agy_prompt("Generate Tests", "Generate comprehensive unit tests covering edge cases for this code", false)
      end, { desc = "AGY Generate Tests (Buffer)" })

      vim.keymap.set("v", "<leader>ag", function()
        run_agy_prompt("Generate Tests", "Generate comprehensive unit tests covering edge cases for this code", true)
      end, { desc = "AGY Generate Tests (Selection)" })
    end,
  },
}
