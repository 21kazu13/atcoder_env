cptlt() {
    local fn
    if [ $# = 0 ]; then
        echo "[ERROR] Specify file name"
        return 1
    elif [ -e $1 ]; then
        echo "[ERROR] File already exist"
        return 1
    fi
    cp ~/.config/atcoder-cli-nodejs/py/main.py $1 &&  code $1
    return $?
}