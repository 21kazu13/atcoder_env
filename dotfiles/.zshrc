# Created by newuser for 5.8

# customize
# language
export LANG=ja_JP.UTF-8

# color
autoload -Uz colors
colors

# prompt & git
# PROMPT='
# %F{cyan}%D{%y/%m/%d} %*%f %~
# $ '
eval "$(oh-my-posh init zsh --config ~/.iterm2.omp.json)"
autoload -Uz compinit && compinit

# Function for atcoder-cli & online-judge-tools
for fn in $(ls ~/scripts/*.sh)
do; source $fn; done

# Clone for remote repository
alias aclone='git clone --depth 1 ${REMOTE} && cd AtCoder'

echo 'Make sure to log-in to atcoder-cli and online-judge-tools.'
echo 'Just execute "aclogin" for both login.'
echo 'Run "aclone" to clone from remote repository after launch.'
