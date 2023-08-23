FROM python:3.11.4 as builder-python

WORKDIR /tmp
COPY req_python-x86_64.txt .
COPY req_python-arm64.txt .

RUN apt update \
    && apt install -y \
        # required from build of online-judge-tools (lxml)
        libxml2-dev \
        libxslt-dev \
        zlib1g-dev 

RUN python -m pip install -U setuptools==66.0.0 wheel \
    && python -m pip wheel -w /tmp/wheels -r req_python-$(uname -m).txt

FROM pypy:3.10-7.3.12 as builder-pypy

RUN apt update \
    && apt install -y --no-install-recommends \
        # ../../meson.build:63:0: ERROR: Unknown compiler(s): [['gfortran'], ['flang'], ['nvfortran'], ['pgfortran'], ['ifort'], ['ifx'], ['g95']]
        gfortran \
        # ../../scipy/meson.build:134:7: ERROR: Dependency "OpenBLAS" not found, tried pkgconfig
        # https://qiita.com/itotomball/items/3ec9eddbe0f6cbab66ad
        libopenblas-dev \
        # src/geos.h:15:10: fatal error: geos_c.h: No such file or directory
        # https://techoverflow.net/2021/08/13/6348/
        libgeos-dev

WORKDIR /tmp
COPY req_pypy.txt .
RUN pypy -m pip install -U setuptools==66.0.0 wheel \
    && pypy -m pip wheel -w /tmp/wheels -r req_pypy.txt
RUN unlink /opt/pypy/bin/python \
    && unlink /opt/pypy/bin/python3 \
    && unlink /opt/pypy/bin/python3.10

FROM node:18 as builder-acc
ENV NODE_OPTIONS=--openssl-legacy-provider
WORKDIR /tmp
RUN git clone https://github.com/Tatamo/atcoder-cli.git
WORKDIR /tmp/atcoder-cli
RUN npm install \
    && npm install -g \
    && npm uninstall -g npm

FROM python:3.11.4-slim as runner

COPY --from=builder-pypy /opt/pypy /usr/local/pypy
RUN ln -s /usr/local/pypy/bin/pypy3 /usr/local/bin/pypy3 \
    && ln -s /usr/local/pypy/bin/pypy /usr/local/bin/pypy 

# For cppyy with MacM1
ENV EXTRA_CLING_ARGS=' -O2'
# https://zenn.dev/yogarasu/articles/425732ff408d06
ENV NODE_OPTIONS=--openssl-legacy-provider

RUN --mount=type=bind,from=builder-python,source=/tmp/wheels,target=/tmp/wheels/python \
    --mount=type=bind,from=builder-pypy,source=/tmp/wheels,target=/tmp/wheels/pypy \
    python -m pip install --no-index --no-deps /tmp/wheels/python/*.whl --no-cache \
    && pypy -m pip install --no-index --no-deps /tmp/wheels/pypy/*.whl --no-cache --no-warn-script-location

RUN apt update \
    && apt install -y --no-install-recommends \
        # required cppyy
        g++ \
        # required numpy, scipy, etc
        libopenblas-dev \
        # required shapely
        libgeos-dev \
        # required from atcoder-cli
        git \
        nodejs \
        time \
        # required from oh-my-posh installation
        curl \
        unzip \
        zsh \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder-acc /tmp/atcoder-cli /tmp/atcoder-cli
COPY --from=builder-acc /usr/local/lib/node_modules /usr/local/lib/node_modules

# hashlib.py:182: RuntimeWarning: The _hashlib module is not available, falling back to a much slower implementation (libssl.so.1.1: cannot open shared object file: No such file or directory
COPY --from=builder-pypy /usr/lib/x86_64-linux-gnu/libssl.so.1.1 /usr/lib/x86_64-linux-gnu/libssl.so.1.1
COPY --from=builder-pypy /usr/lib/x86_64-linux-gnu/libcrypto.so.1.1 /usr/lib/x86_64-linux-gnu/libcrypto.so.1.1

RUN ln -s /usr/local/lib/node_modules/atcoder-cli/bin/index.js /usr/local/bin/acc

# Install for oh-my-posh
RUN curl -s https://ohmyposh.dev/install.sh | bash -s 

# Timezone Setting for Debian GNU/Linux 10
# Ref: https://qiita.com/pyon_kiti_jp/items/e9235f9f49430bb845bb
ARG TZ=Asia/Tokyo
RUN ln -s -f /usr/share/zoneinfo/$TZ /etc/localtime 
RUN echo $TZ | tee /etc/timezone >/dev/null
ENV TZ=$TZ

# Create a non-root user to use if preferred - see https://aka.ms/vscode-remote/containers/non-root-user.
# https://unit42.paloaltonetworks.jp/non-root-containers-kubernetes-cve-2019-11245-care/
# https://qiita.com/syoyo/items/6fa6597b7a6625000e33
ARG USERNAME=vscode
ARG USERPASSWD=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME:$USERPASSWD | chpasswd 
# Add sudo support for non-root user
    # && echo $USERNAME ALL=\(ALL\) ALL >> /etc/sudoers.d/$USERNAME \
    # && chmod 0440 /etc/sudoers.d/$USERNAME

# Working directory for 'RUN', 'CMD', 'ENTRYPOINT, 'COPY', 'ADD'
# https://docs.docker.jp/engine/reference/builder.html#workdir
USER $USERNAME
WORKDIR /home/$USERNAME

# COPY setting files from host
# COPY --chown=$USERNAME ./dotfiles/.zshrc /home/$USERNAME/
# COPY --chown=$USERNAME:$USERNAME templates/atcoder-cli-nodejs/ /home/$USERNAME/.config/atcoder-cli-nodejs/
# COPY --chown=$USERNAME ./dotfiles/.iterm2.omp.json /home/$USERNAME/

# change default shell
ENV SHELL=/usr/bin/zsh

# Enable atcoder-cli configuration
RUN acc config default-template py \
    && acc config default-task-choice all \
    && acc config default-test-dirname-format test 

# # Enable git configuration
# ARG GITNAME
# ARG GITEMAIL
# RUN git config --global user.name $GITNAME \
#     && git config --global user.email $GITEMAIL

# test
RUN python -c 'import \
                    cppyy, \
                    numpy, \
                    scipy, \
                    networkx, \
                    sympy, \
                    sortedcontainers, \
                    more_itertools, \
                    shapely, \
                    bitarray, \
                    pulp, \
                    mpmath, \
                    pandas, \
                    z3, \
                    sklearn, \
                    ortools, \
                    torch, \
                    polars, \
                    lightgbm, \
                    gmpy2, \
                    numba, \
                    atcoder' \
    && pypy -c 'import \
                    cppyy, \
                    numpy, \
                    scipy, \
                    networkx, \
                    sympy, \
                    sortedcontainers, \
                    more_itertools, \
                    shapely, \
                    bitarray, \
                    pulp, \
                    mpmath, \
                    pandas, \
                    z3, \
                    sklearn, \
                    typing_extensions, \
                    atcoder' \
    && oj --help \
    && acc config \
    && acc check-oj
