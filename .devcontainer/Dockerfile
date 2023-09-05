# Declear common argument among multi stages
# https://qiita.com/ktooi/items/9c12802deb52eccf0858
ARG CERT_PATH=/etc/ssl/certs/ca-certificates.crt
ARG CERT_DIR=/etc/ssl/certs/

###############################################################
### Create and prepare self signed certificate for netscope ###
###############################################################
# Install first, then copy and use /etc/ssl/certs/ca-certificates.crt into other stages
# https://stakiran.hatenablog.com/entry/2018/06/12/213727
# http://www.maibun.org/~nt/technicalnote/centos8/ssl4.html
# https://qiita.com/kusanoiskuzuno/items/cf35b65a3c42c11be67c
# https://qiita.com/hi-naoya/items/d325a57d24a39e4d03e8
FROM ubuntu:22.10 as cert
COPY dotfiles/* /usr/share/ca-certificates/extra/
RUN apt update && \
    apt-get install -y ca-certificates
RUN if [ -e /usr/share/ca-certificates/extra/nscacert.pem ]; then \
        # update-ca-certificates will fail without this.
        # http://www.maibun.org/~nt/technicalnote/centos8/ssl4.html
        echo 'extra/nscacert.pem' >> /etc/ca-certificates.conf ; \
    fi
RUN update-ca-certificates

#####################################
### Build python3.11.4 pip wheels ###
#####################################
FROM python:3.11.4 as builder-python
WORKDIR /tmp
COPY requirement/req_python-*.txt .

RUN apt update \
    && apt install -y \
        # required from build of gmpy2
        libmpfr-dev \
        libgmp-dev \
        libmpc-dev \
        # required from build of online-judge-tools (lxml)
        libxml2-dev \
        libxslt-dev \
        zlib1g-dev 

# copy cert and set environment valuables for pip
ARG CERT_PATH
ARG CERT_DIR
COPY --from=cert $CERT_PATH $CERT_PATH
ENV CERT_PATH=${CERT_PATH}
ENV SSL_CERT_FILE=${CERT_PATH}
ENV REQUESTS_CA_BUNDLE=${CERT_PATH}
ENV CERT_DIR=${CERT_DIR}
ENV SSL_CERT_DIR=${CERT_DIR}

RUN python -m pip install -U setuptools==66.0.0 wheel \
    && python -m pip wheel -w /tmp/wheels -r req_python-$(uname -m).txt
# Current pip version and z3-solver is not supported aarch64 wheels (just file name issue?)
# https://oregengo.hatenablog.com/entry/2016/12/20/175835
# from pip._internal.utils.compatibility_tags import get_supported
RUN UNAME=$(uname -m) \
    && case ${UNAME} in \
        aarch64 ) mv wheels/z3_solver-4.12.1.0-py2.py3-none-manylinux1_aarch64.whl wheels/z3_solver-4.12.1.0-py2.py3-none-linux_aarch64.whl;; \
    esac

# separate support tools from runtime packages.
COPY requirement/req_support_python.txt .
RUN python -m pip wheel -w /tmp/wheels -r req_support_python.txt

#################################
### Build pypy3.10 pip wheels ###
#################################
FROM ubuntu:22.10 as builder-pypy

# copy cert and set environment valuables for pip
ARG CERT_PATH
ARG CERT_DIR
COPY --from=cert $CERT_PATH $CERT_PATH
ENV CERT_PATH=${CERT_PATH}
ENV SSL_CERT_FILE=${CERT_PATH}
ENV REQUESTS_CA_BUNDLE=${CERT_PATH}
ENV CERT_DIR=${CERT_DIR}
ENV SSL_CERT_DIR=${CERT_DIR}

RUN apt update \
    && apt install -y --no-install-recommends \
        # for cppyy with python runtime, g++ should be g++12
        git wget bzip2 \
        gcc g++ gfortran libopenblas-dev liblapack-dev pkg-config libgeos-dev \
        # python3 and build-essential is required for cppyy installation
        build-essential python3 \
        vim sudo

# install pypy from the source, for cppyy with python runtime, g++ should be g++12
# # since pypy:3.10-7.3.12 is working with g++10, then it causes following error
# # ERROR in cling::CIFactory::createCI(): cannot extract standard library include paths!
WORKDIR /
ARG TARGETPLATFORM
RUN TARGETPYPY=$( \
        case ${TARGETPLATFORM} in \
            linux/amd64 ) echo "linux64";; \
            linux/arm64 ) echo "aarch64";; \
        esac \
    ) && \
    wget https://downloads.python.org/pypy/pypy3.10-v7.3.12-${TARGETPYPY}.tar.bz2 \
    && tar -xvf pypy3.10-v7.3.12-${TARGETPYPY}.tar.bz2 -C /usr/local \
    && ln -s /usr/local/pypy3.10-v7.3.12-${TARGETPYPY}/bin/pypy3 /usr/local/bin/pypy3 \
    && ln -s /usr/local/pypy3.10-v7.3.12-${TARGETPYPY}/bin/pypy /usr/local/bin/pypy \
    && wget https://bootstrap.pypa.io/get-pip.py \
    && pypy3 get-pip.py --break-system-packages 

WORKDIR /tmp
COPY requirement/req_pypy.txt .

RUN pypy -m pip install -U setuptools==66.0.0 wheel \
    && pypy -m pip wheel -w /tmp/wheels -r req_pypy.txt

# Current pip version and z3-solver is not supported aarch64 wheels (just file name issue?)
# https://oregengo.hatenablog.com/entry/2016/12/20/175835
# from pip._internal.utils.compatibility_tags import get_supported
RUN UNAME=$(uname -m) \
    && case ${UNAME} in \
        aarch64 ) mv wheels/z3_solver-4.12.1.0-py2.py3-none-manylinux1_aarch64.whl wheels/z3_solver-4.12.1.0-py2.py3-none-linux_aarch64.whl;; \
    esac

##########################################
### Build npm packages for atcoder-cli ###
##########################################
FROM node:18 as builder-acc
# atcoder-cli seems to be using old openssl
# https://zenn.dev/yogarasu/articles/425732ff408d06
ENV NODE_OPTIONS=--openssl-legacy-provider

# copy cert and set environment valuables for npm
ARG CERT_PATH
ARG CERT_DIR
COPY --from=cert $CERT_PATH $CERT_PATH

# currently acc is not supported "-l" option in production build
# clone develop branch directly build then we can select python3.11.4 directly
WORKDIR /tmp
RUN git clone https://github.com/Tatamo/atcoder-cli.git
WORKDIR /tmp/atcoder-cli
RUN npm install \
    && npm install -g \
    && npm uninstall -g npm

########################
### Build main stage ###
########################
FROM python:3.11.4-slim as runner

# copy pypy3 runtime
ARG TARGETPLATFORM
RUN --mount=type=bind,from=builder-pypy,source=/usr/local,target=/tmp/ \
    TARGETPYPY=$( \
        case ${TARGETPLATFORM} in \
            linux/amd64 ) echo "linux64";; \
            linux/arm64 ) echo "aarch64";; \
        esac \
    ) \
    && cp -r /tmp/pypy3.10-v7.3.12-${TARGETPYPY} /usr/local/ \
    && ln -s /usr/local/pypy3.10-v7.3.12-${TARGETPYPY}/bin/pypy3 /usr/local/bin/pypy3 \
    && ln -s /usr/local/pypy3.10-v7.3.12-${TARGETPYPY}/bin/pypy /usr/local/bin/pypy 

# For cppyy with MacM1
# cppyy-backend https://github.com/wlav/cppyy-backend/blob/master/cling/python/cppyy_backend/loader.py
# when CURRENT_ARGS += ' -O2 -march=native' selected, import fails
ENV EXTRA_CLING_ARGS=' -O2'

# Install some required packages
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
        # required my usage in container
        zsh \
        ssh \
        # sudo \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# copy packages from atcoder-cli build
COPY --from=builder-acc /tmp/atcoder-cli /tmp/atcoder-cli
COPY --from=builder-acc /usr/local/lib/node_modules /usr/local/lib/node_modules

# copy cert and set environment valuables for pip, atcoder-cli, oj
ARG CERT_PATH
ARG CERT_DIR
COPY --from=cert $CERT_PATH $CERT_PATH
ENV CERT_PATH=${CERT_PATH}
ENV SSL_CERT_FILE=${CERT_PATH}
ENV CERT_DIR=${CERT_DIR}
ENV SSL_CERT_DIR=${CERT_DIR}
# https://help.zscaler.com/ja/zia/adding-custom-certificate-application-specific-trust-store
ENV REQUESTS_CA_BUNDLE=${CERT_PATH}
# https://help.zscaler.com/ja/zia/adding-custom-certificate-application-specific-trust-store
ENV NODE_EXTRA_CA_CERTS=${CERT_PATH}

# create cymbolic link for using atcoder-cli globally
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
    # # Add sudo support for non-root user
    # && echo $USERNAME ALL=\(ALL\) ALL >> /etc/sudoers.d/$USERNAME \
    # && chmod 0440 /etc/sudoers.d/$USERNAME

# Working directory for 'RUN', 'CMD', 'ENTRYPOINT, 'COPY', 'ADD'
# https://docs.docker.jp/engine/reference/builder.html#workdir
USER $USERNAME
WORKDIR /home/$USERNAME

# copy wheels from pypy / python
ENV PATH=$PATH:/home/$USERNAME/.local/bin
RUN --mount=type=bind,from=builder-python,source=/tmp/wheels,target=/tmp/wheels/python \
    --mount=type=bind,from=builder-pypy,source=/tmp/wheels,target=/tmp/wheels/pypy \
    python -m pip install --no-index --no-deps /tmp/wheels/python/*.whl --no-cache --user\
    && pypy -m pip install --no-index --no-deps /tmp/wheels/pypy/*.whl --no-cache --no-warn-script-location --user

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
