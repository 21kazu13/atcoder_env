cptlt() {
    local fn
    if [ $# = 0 ]; then
        fn=$(date +%Y%m%d).py
    else
        fn=$1
    fi
    if [ -e $fn ]; then
        echo "[ERROR] File already exist"
        return 1
    fi
    cp ~/.config/atcoder-cli-nodejs/py/main.py $fn && code $fn
    return $?
}