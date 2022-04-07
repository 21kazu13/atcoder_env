#!/usr/bin/zsh

# reference
# https://kagamilove0707.hatenablog.com/entry/2014/04/08/011043
# https://www.server-memo.net/shellscript/file_check.html
# https://shellscript.sunone.me/if_and_test.html
# https://github.com/Tatamo/atcoder-cli/issues/29

# Note that source this file before using below functions.

ojt() {
    local fn
    if [ $# = 0 ]; then
        fn="main.py"
    elif [ ! -e $1 ]; then
        echo "File not exist"
        return 1
    else
        local fn=$1
    fi
    # echo "filename check OK: ${fn}"
    local str="python ${fn}"
    oj t -c $str
    return 0
}

ojtpypy() {
    local fn
    if [ $# = 0 ]; then
        fn="main.py"
    elif [ ! -e $1 ]; then
        echo "File not exist"
        return 1
    else
        local fn=$1
    fi
    # echo "filename check OK: ${fn}"
    local str="pypy3 ${fn}"
    oj t -c $str
    return 0
}

accpypy() {
    local fn
    if [ $# = 0 ]; then
        fn="main.py"
    elif [ ! -e $1 ]; then
        echo "File not exist"
        return 1
    else
        local fn=$1
    fi
    acc s $fn -- --guess-python-interpreter pypy
}
