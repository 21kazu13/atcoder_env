#! /usr/bin/zsh

aclogin(){
    local URL=https://atcoder.jp/login
    acc login
    oj login -u $ACUSER $URL
}
