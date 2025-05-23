# Declear common argument among multi stages
# https://qiita.com/ktooi/items/9c12802deb52eccf0858
ARG AC_PYPY_VERSION=3.10-v7.3.19
ARG AC_CPYTHON_VERSION=3.13.3

#####################################
### Build python3.13.3 pip wheels ###
#####################################
FROM ubuntu:24.04 AS builder-python
ARG AC_CPYTHON_VERSION

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

WORKDIR /tmp
ARG TARGETPYTHON="Python-${AC_CPYTHON_VERSION}"
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    build-essential gdb lcov pkg-config \
    libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev \
    libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev \
    lzma lzma-dev tk-dev uuid-dev zlib1g-dev git wget libgmp-dev libmpfr-dev libmpc-dev \
    && wget -q https://www.python.org/ftp/python/"${AC_CPYTHON_VERSION}"/"${TARGETPYTHON}".tar.xz -O "${TARGETPYTHON}".tar.xz \
    && tar xf "${TARGETPYTHON}".tar.xz

WORKDIR /tmp/${TARGETPYTHON}

RUN ./configure --enable-optimizations --with-lto=full --with-strict-overflow \
    && make -j"$(nproc)" \
    && make altinstall

WORKDIR /tmp
COPY requirement/req_python.txt .
COPY requirement/req_support_python.txt .

# installing cppyy may fail when setuptools is not up to date
RUN python3.13 -m pip install --no-cache-dir setuptools==75.8.0 \
    && python3.13 -m pip install --no-deps --no-cache-dir -r req_python.txt --no-warn-script-location \
    && python3.13 -m pip install --no-deps --no-cache-dir torch==2.6.0+cpu --index-url https://download.pytorch.org/whl/cpu --no-warn-script-location \
    && wget -q -O numba.tar.gz https://files.pythonhosted.org/packages/1c/a0/e21f57604304aa03ebb8e098429222722ad99176a4f979d34af1d1ee80da/numba-0.61.2.tar.gz \
    && mkdir numba \
    && tar -C numba --strip-components=1 -xf numba.tar.gz \
    && sed -i 's/ext_cuda_extras, //' numba/setup.py \
    && rm -fr numba/numba/cuda \
    && python3.13 -m pip install --no-cache-dir ./numba/ \
    && python3.13 -m pip install --no-cache-dir -r req_support_python.txt --no-warn-script-location

#################################
### Build pypy3.10 pip wheels ###
#################################
FROM ubuntu:24.04 AS builder-pypy
ARG AC_PYPY_VERSION
WORKDIR /tmp
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        # vim sudo
        git wget bzip2 \
        build-essential gfortran libopenblas-dev liblapack-dev pkg-config libgeos-dev \
        #  fatal: unable to access 'https://github.com/not522/ac-library-python/': server certificate verification failed. CAfile: none CRLfile: none
        ca-certificates

COPY requirement/req_pypy.txt .

ARG TARGETPLATFORM
RUN TARGETPYPY=$( \
        case "${TARGETPLATFORM}" in \
            linux/amd64 ) echo "pypy${AC_PYPY_VERSION}-linux64";; \
            linux/arm64 ) echo "pypy${AC_PYPY_VERSION}-aarch64";; \
        esac \
    ) && \
    wget -q https://downloads.python.org/pypy/"${TARGETPYPY}".tar.bz2 \
    && tar jxvf "${TARGETPYPY}".tar.bz2 \
    && export PATH="$PATH":/tmp/"${TARGETPYPY}"/bin \
    # activate pip
    # https://docs.python.org/ja/3.13/library/ensurepip.html
    && pypy3 -m ensurepip --upgrade --altinstall \
    # Setuptools最新化
    && pypy3 -m pip install setuptools==75.8.0\
    && pypy3 -m pip install -r req_pypy.txt --no-warn-script-location \
    && unlink ./"${TARGETPYPY}"/bin/python \
    && unlink ./"${TARGETPYPY}"/bin/python3 \
    && unlink ./"${TARGETPYPY}"/bin/python3.10

##########################################
### Build npm packages for atcoder-cli ###
##########################################
FROM node:22-slim AS builder-acc
# atcoder-cli seems to be using old openssl
# https://zenn.dev/yogarasu/articles/425732ff408d06
ENV NODE_OPTIONS=--openssl-legacy-provider

# currently acc is not supported "-l" option in production build
# clone develop branch directly build then we can select python3.11.4 directly
WORKDIR /usr/local/src
# https://qiita.com/nossy/items/0f5572d84f4617207378
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update \
    && apt-get install -y --no-install-recommends git curl unzip \
    && curl -s https://ohmyposh.dev/install.sh | bash -s -- -d /usr/local/bin \
    && git clone https://github.com/Tatamo/atcoder-cli.git
WORKDIR /usr/local/src/atcoder-cli
RUN npm install \
    && npm install -g \
    && npm uninstall -g npm

########################
### Build main stage ###
########################
FROM ubuntu:24.04 AS runner

ARG AC_PYPY_VERSION
ARG AC_CPYTHON_VERSION
# copy python3 runtime
COPY --from=builder-python /usr/local /usr/local
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# copy pypy3 runtime
ARG TARGETPLATFORM
RUN --mount=type=bind,from=builder-pypy,source=/tmp,target=/tmp/ \
    TARGETPYPY=$( \
        case "${TARGETPLATFORM}" in \
            linux/amd64 ) echo "pypy${AC_PYPY_VERSION}-linux64";; \
            linux/arm64 ) echo "pypy${AC_PYPY_VERSION}-aarch64";; \
        esac \
    ) \
    && cp -r /tmp/"${TARGETPYPY}"/bin/* /usr/local/bin \
    && cp -r /tmp/"${TARGETPYPY}"/lib/* /usr/local/lib \
    && cp -r /tmp/"${TARGETPYPY}"/include/* /usr/local/include \
    && ln -s /usr/local/bin/python3.13 /usr/local/bin/python \
    && ln -s /usr/local/bin/python3.13 /usr/local/bin/python3

# Install some required packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        # required cppyy
        g++ \
        # required numpy, scipy, etc
        libopenblas-dev \
        # required shapely
        libgeos-dev \
        # required from atcoder-cli
        nodejs \
        time \
        # required my usage in container
        zsh \
        ssh \
        git \
        # sudo \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# copy packages from atcoder-cli build
COPY --from=builder-acc /usr/local/src/atcoder-cli /usr/local/src/atcoder-cli
COPY --from=builder-acc /usr/local/bin/oh-my-posh /usr/local/bin/oh-my-posh
COPY --from=builder-acc /usr/local/lib/node_modules /usr/local/lib/node_modules

# create cymbolic link for using atcoder-cli globally
RUN ln -s /usr/local/lib/node_modules/atcoder-cli/bin/index.js /usr/local/bin/acc

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
# https://askubuntu.com/questions/1513927/ubuntu-24-04-docker-images-now-includes-user-ubuntu-with-uid-gid-1000
ARG USER_UID=1000
ARG USER_GID=$USER_UID
# https://github.com/devcontainers/images/issues/1056#issuecomment-2160102633
RUN userdel -r ubuntu \
    && groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME:$USERPASSWD | chpasswd 
    # # Add sudo support for non-root user
    # && echo $USERNAME ALL=\(ALL\) ALL >> /etc/sudoers.d/$USERNAME \
    # && chmod 0440 /etc/sudoers.d/$USERNAME

# Working directory for 'RUN', 'CMD', 'ENTRYPOINT, 'COPY', 'ADD'
# https://docs.docker.jp/engine/reference/builder.html#workdir
USER $USERNAME
WORKDIR /home/$USERNAME

# COPY setting files from host
COPY --chown=$USERNAME ./dotfiles/.zshrc /home/$USERNAME/
COPY --chown=$USERNAME:$USERNAME templates/atcoder-cli-nodejs/ /home/$USERNAME/.config/atcoder-cli-nodejs/
COPY --chown=$USERNAME ./dotfiles/.iterm2.omp.json /home/$USERNAME/

# change default shell
ENV SHELL=/usr/bin/zsh

# Enable atcoder-cli configuration
RUN acc config default-template py \
    && acc config default-task-choice all \
    && acc config default-test-dirname-format test 

# Enable git configuration
ARG GITNAME
ARG GITEMAIL
RUN git config --global user.name $GITNAME \
    && git config --global user.email $GITEMAIL

# # test
RUN python -c 'import \
                atcoder, \
                acl_cpp, \
                bitarray, \
                cppyy, \ 
                cython, \
                gmpy2, \
                lightgbm, \
                more_itertools, \
                ortools, \
                polars, \
                pulp, \
                pyrsistent, \
                rustworkx, \
                sklearn, \
                shapely, \
                sortedcontainers, \
                torch, \
                numpy, \
                scipy' \
    && python -c 'from numba import jit' \
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
                    acl_cpp, \
                    atcoder' \
    && oj --help \
    && acc config \
    && acc check-oj

    CMD [ "zsh" ]
