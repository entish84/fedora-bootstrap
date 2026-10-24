# =============================================================================
# 1. ENVIRONMENT & PATH
# =============================================================================
export LANG=en_US.UTF-8
export EDITOR=micro
export VISUAL=micro

# Smart word deletion (Alt+Backspace stops at '/', '.', '-', '_')
WORDCHARS=${WORDCHARS//[\/.-_]}

typeset -U path
path=(
    "$HOME/.local/bin"
    "$HOME/bin"
    "/usr/local/bin"
    $path
)
export PATH

# =============================================================================
# 2. THEME COHESION: FZF, BAT & AUTOSUGGESTIONS (#222831 / #393e46 / #ffd369)
# =============================================================================
export FZF_DEFAULT_OPTS=" \
  --height=45% --layout=reverse --border=rounded --margin=0,1 \
  --prompt='❱ ' --pointer='❱' --marker='✓' \
  --color=bg+:#393e46,bg:#222831,spinner:#ffd369,hl:#ffd369 \
  --color=fg:#abb2bf,header:#61afef,info:#7f848e,pointer:#ffd369 \
  --color=marker:#98c379,fg+:#eeeeee,prompt:#ffd369,hl+:#ffd369 \
  --color=border:#393e46,label:#ffd369,query:#eeeeee"

export BAT_THEME="TwoDark"
export ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE="fg=#5c6370"
export ZSH_AUTOSUGGEST_STRATEGY=(history completion)
export ZSH_AUTOSUGGEST_BUFFER_MAX_SIZE=20

# =============================================================================
# 3. HISTORY CONFIGURATION (Optimized for Zsh + Atuin)
# =============================================================================
HISTFILE="$HOME/.zhistory"
SAVEHIST=100000
HISTSIZE=100000

setopt EXTENDED_HISTORY          # Record timestamp in history
setopt SHARE_HISTORY             # Share history between all sessions
setopt HIST_IGNORE_ALL_DUPS      # Delete old recorded entry if new entry is a duplicate
setopt HIST_IGNORE_SPACE         # Do not record an entry starting with a space
setopt HIST_REDUCE_BLANKS        # Remove superfluous blanks before recording entry
setopt HIST_VERIFY               # Show command with history expansion before running
setopt AUTO_CD                   # Type directory name to cd into it
setopt INTERACTIVE_COMMENTS      # Allow # comments in interactive shell

# =============================================================================
# 4. ZINIT BOOTSTRAP & ANNEXES
# =============================================================================
ZINIT_HOME="${XDG_DATA_HOME:-${HOME}/.local/share}/zinit/zinit.git"
if [[ ! -d "$ZINIT_HOME" ]]; then
    mkdir -p "$(dirname "$ZINIT_HOME")"
    git clone https://github.com/zdharma-continuum/zinit.git "$ZINIT_HOME"
fi
source "${ZINIT_HOME}/zinit.zsh"

zinit light-mode for \
    zdharma-continuum/zinit-annex-as-monitor \
    zdharma-continuum/zinit-annex-bin-gem-node \
    zdharma-continuum/zinit-annex-patch-dl \
    zdharma-continuum/zinit-annex-rust

# =============================================================================
# 5. OH-MY-ZSH SNIPPETS & PLUGINS (Turbo Loaded)
# =============================================================================
zstyle ':omz:plugins:eza' 'dirs-first' yes
zstyle ':omz:plugins:eza' 'git-status' yes
zstyle ':omz:plugins:eza' 'header' yes
zstyle ':omz:plugins:eza' 'icons' yes

# Load essential directory & git helpers in Turbo mode for <15ms startup
zinit wait'0' lucid for \
    OMZL::git.zsh \
    OMZL::directories.zsh \
    OMZP::git \
    OMZP::direnv \
    OMZP::eza

# =============================================================================
# 6. COMPLETIONS, FZF-TAB & SYNTAX HIGHLIGHTING (Strict Load Order: 0a -> 0b -> 0c)
# =============================================================================
# Step 0: Additional completion definitions
zinit ice wait'0' lucid blockf
zinit light zsh-users/zsh-completions

# Step 0a: Initialize compinit FIRST, then load fzf-tab BEFORE widget wrappers
zinit ice wait'0a' lucid atinit"ZINIT[COMPINIT_OPTS]=-C; zicompinit; zicdreplay"
zinit light Aloxaf/fzf-tab

# Step 0b: Fast Syntax Highlighting (loads after fzf-tab)
zinit ice wait'0b' lucid
zinit light zdharma-continuum/fast-syntax-highlighting

# Step 0c: Autosuggestions + Keybindings (loads last to wrap widgets cleanly)
zinit ice wait'0c' lucid atload"!_zsh_autosuggest_start; bindkey '^ ' autosuggest-accept; bindkey '^f' autosuggest-accept"
zinit light zsh-users/zsh-autosuggestions

# =============================================================================
# 7. FZF-TAB & COMPLETION STYLING
# =============================================================================
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}' 'r:|[._-]=* r:|=*' 'l:|=* r:|=*'
zstyle ':completion:*:descriptions' format '[%d]'
zstyle ':completion:*' list-colors ${(s.:.)LS_COLORS}
zstyle ':completion:*:git-checkout:*' sort false

# Make fzf-tab inherit our custom #222831 / #ffd369 FZF_DEFAULT_OPTS
zstyle ':fzf-tab:*' use-fzf-default-opts yes
zstyle ':fzf-tab:*' switch-group ',' '.'

# Preview: cd (Directory tree with icons)
zstyle ':fzf-tab:complete:cd:*' fzf-preview 'eza -1 --icons --group-directories-first --color=always $realpath'
zstyle ':fzf-tab:complete:z:*' fzf-preview 'eza -1 --icons --group-directories-first --color=always $realpath'

# Preview: kill / ps (Process details)
zstyle ':completion:*:*:*:*:processes' command "ps -u $USER -o pid,user,comm -w -w"
zstyle ':fzf-tab:complete:(kill|ps):argument-rest' fzf-preview \
  '[[ $group == "[process ID]" ]] && ps --pid=$word -o cmd --no-headers -w -w'
zstyle ':fzf-tab:complete:(kill|ps):argument-rest' fzf-flags --preview-window=down:3:wrap

# Preview: Environment Variables
zstyle ':fzf-tab:complete:(-command-|-parameter-|-brace-parameter-|export|unset|expand):*' \
  fzf-preview 'echo ${(P)word}'

# Preview: Systemd status
zstyle ':fzf-tab:complete:systemctl-*:*' fzf-preview 'SYSTEMD_COLORS=1 systemctl status $word'

# Preview: General files & directories (eza for dirs, bat for files)
zstyle ':fzf-tab:complete:*:*' fzf-preview \
  'if [[ -d $realpath ]]; then eza -1 --icons --group-directories-first --color=always $realpath; elif [[ -f $realpath ]]; then bat --color=always --style=numbers --line-range :500 $realpath 2>/dev/null; fi'

# =============================================================================
# 8. CLI TOOLS INITIALIZATION (Starship, Mise, Zoxide, FZF, Atuin)
# =============================================================================
[[ -f "$HOME/.atuin/bin/env" ]] && . "$HOME/.atuin/bin/env"

# 1. Starship Prompt
if command -v starship >/dev/null 2>&1; then
    eval "$(starship init zsh)"
fi

# 2. Mise (Polyglot runtime manager)
if command -v mise >/dev/null 2>&1; then
    eval "$(mise activate zsh)"
fi

# 3. Zoxide (Smart directory jumper)
if command -v zoxide >/dev/null 2>&1; then
    eval "$(zoxide init zsh)"
fi

# 4. FZF native keybindings (Ctrl+T for files, Alt+C for dirs; Atuin overrides Ctrl+R next)
if command -v fzf >/dev/null 2>&1; then
    source <(fzf --zsh 2>/dev/null)
fi

# 5. Atuin (Shell history — loaded after fzf so Atuin owns Ctrl+R and Up-Arrow)
if command -v atuin >/dev/null 2>&1; then
    eval "$(atuin init zsh)"
fi

# =============================================================================
# 9. SUBTLE TRANSIENT PROMPT (Collapses executed lines to "∙ ❱ ")
# =============================================================================
_TransientPrompt_zle-line-init() {
    emulate -L zsh
    [[ $CONTEXT == start ]] || return 0
    while true; do
        zle .recursive-edit
        local -i ret=$?
        [[ $ret == 0 && $KEYS == $'\4' ]] || break
        [[ -o ignore_eof ]] || exit 0
    done
    local saved_prompt=$PROMPT
    local saved_rprompt=$RPROMPT
    PROMPT='%F{#7f848e}∙%f %F{#ffd369}❱%f '
    RPROMPT=''
    zle .reset-prompt
    PROMPT=$saved_prompt
    RPROMPT=$saved_rprompt
    if (( ret )); then
        zle .send-break
    else
        zle .accept-line
    fi
    return ret
}
zle -N zle-line-init _TransientPrompt_zle-line-init

# =============================================================================
# 10. FUNCTIONS, ALIASES & TERMINAL INTEGRATION
# =============================================================================
# Yazi file manager wrapper (changes CWD on exit)
function yy() {
    local tmp="$(mktemp -t "yazi-cwd.XXXXXX")"
    yazi "$@" --cwd-file="$tmp"
    if cwd="$(cat -- "$tmp")" && [[ -n "$cwd" ]] && [[ "$cwd" != "$PWD" ]]; then
        builtin cd -- "$cwd"
    fi
    rm -f -- "$tmp"
}

alias fm='yy'

# Kitty SSH fix (propagates terminfo automatically to remote servers)
[[ "$TERM" == "xterm-kitty" ]] && alias ssh='kitten ssh'

# Custom external aliases
[[ -f ~/.zsh_aliases ]] && source ~/.zsh_aliases

# VS Code shell integration
[[ "$TERM_PROGRAM" == "vscode" ]] && command -v code >/dev/null 2>&1 && . "$(code --locate-shell-integration-path zsh)"

# Path additions
export PATH="$HOME/.local/bin:$PATH"
