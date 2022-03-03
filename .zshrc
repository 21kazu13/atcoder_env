# Created by newuser for 5.8

#customize
#language
export LANG=ja_JP.UTF-8

#color
autoload -Uz colors
colors

##prompt
PROMPT='
%F{cyan}%D{%y/%m/%d} %*%f %~
$ '

alias ojt='oj t -c \"python main.py\"'
echo 'Make sure to log-in to atcoder-cli and online-judge-tools.'
/tmp/login.sh