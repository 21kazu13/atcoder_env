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

RUN apt-get update
RUN apt-get install -y build-essential gdb lcov pkg-config \
    libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev \
    libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev \
    lzma lzma-dev tk-dev uuid-dev zlib1g-dev git wget libgmp-dev libmpfr-dev libmpc-dev 

WORKDIR /tmp

RUN wget -q https://www.python.org/ftp/python/${AC_CPYTHON_VERSION}/Python-${AC_CPYTHON_VERSION}.tar.xz -O Python-${AC_CPYTHON_VERSION}.tar.xz \
   && tar xf Python-${AC_CPYTHON_VERSION}.tar.xz

WORKDIR /tmp/Python-${AC_CPYTHON_VERSION}

RUN ./configure --enable-optimizations --with-lto=full --with-strict-overflow \
    && make -j$(nproc) \
    && make altinstall

WORKDIR /tmp
COPY requirement/req_python.txt .

# installing cppyy may fail when setuptools is not up to date
RUN python3.13 -m pip install setuptools==75.8.0 \
    && python3.13 -m pip install --no-deps -r req_python.txt --no-warn-script-location \
    && python3.13 -m pip install --no-deps torch==2.6.0+cpu --index-url https://download.pytorch.org/whl/cpu --no-warn-script-location \
    && wget -q -O numba.tar.gz https://files.pythonhosted.org/packages/1c/a0/e21f57604304aa03ebb8e098429222722ad99176a4f979d34af1d1ee80da/numba-0.61.2.tar.gz \
    && mkdir numba \
    && tar -C numba --strip-components=1 -xf numba.tar.gz

WORKDIR /tmp/numba
RUN sed -i 's/ext_cuda_extras, //' setup.py \
    && RUN rm -fr numba/cuda \
    && python3.13 -m pip install . \
# clean up
    && python3.13 -m pip cache purge


#################################
### Build pypy3.10 pip wheels ###
#################################
FROM ubuntu:24.04 AS builder-pypy
ARG AC_PYPY_VERSION
WORKDIR /tmp
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        # # for cppyy with python runtime, g++ should be g++12
        # git wget bzip2 \
        # gcc g++ gfortran libopenblas-dev liblapack-dev pkg-config libgeos-dev \
        # # python3 and build-essential is required for cppyy installation
        # build-essential python3 \
        # vim sudo
        git wget bzip2 \
        build-essential gfortran libopenblas-dev liblapack-dev pkg-config libgeos-dev \
        #  fatal: unable to access 'https://github.com/not522/ac-library-python/': server certificate verification failed. CAfile: none CRLfile: none
        ca-certificates

# install pypy from the source, for cppyy with python runtime, g++ should be g++12
# # since pypy:3.10-7.3.12 is working with g++10, then it causes following error
# # ERROR in cling::CIFactory::createCI(): cannot extract standard library include paths!
ARG TARGETPLATFORM
RUN TARGETPYPY=$( \
        case ${TARGETPLATFORM} in \
            linux/amd64 ) echo "linux64";; \
            linux/arm64 ) echo "aarch64";; \
        esac \
    ) && \
    wget -q https://downloads.python.org/pypy/pypy${AC_PYPY_VERSION}-${TARGETPYPY}.tar.bz2 \
    && tar jxvf pypy${AC_PYPY_VERSION}-${TARGETPYPY}.tar.bz2 \
    # activate pip
    # https://docs.python.org/ja/3.13/library/ensurepip.html
    && ./pypy${AC_PYPY_VERSION}-${TARGETPYPY}/bin/pypy3 -m ensurepip --upgrade --altinstall \
    # Setuptools最新化
    && ./pypy${AC_PYPY_VERSION}-${TARGETPYPY}/bin/pypy3 -m pip install setuptools==75.8.0 

COPY requirement/req_pypy.txt .

RUN TARGETPYPY=$( \
        case ${TARGETPLATFORM} in \
            linux/amd64 ) echo "linux64";; \
            linux/arm64 ) echo "aarch64";; \
        esac \
    ) && \
    export PATH=$PATH:/tmp/pypy${AC_PYPY_VERSION}-${TARGETPYPY}/bin \
    && ./pypy${AC_PYPY_VERSION}-${TARGETPYPY}/bin/pypy3.10 -m pip install --no-deps -r req_pypy.txt --no-warn-script-location \
    && unlink ./pypy${AC_PYPY_VERSION}-${TARGETPYPY}/bin/python \
    && unlink ./pypy${AC_PYPY_VERSION}-${TARGETPYPY}/bin/python3 \
    && unlink ./pypy${AC_PYPY_VERSION}-${TARGETPYPY}/bin/python3.10

##########################################
### Build npm packages for atcoder-cli ###
##########################################
FROM node:18 AS builder-acc
# atcoder-cli seems to be using old openssl
# https://zenn.dev/yogarasu/articles/425732ff408d06
ENV NODE_OPTIONS=--openssl-legacy-provider

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
FROM ubuntu:24.04 AS runner

ARG AC_PYPY_VERSION
ARG AC_CPYTHON_VERSION
# copy python3 runtime
COPY --from=builder-python /usr/local /usr/local

# copy pypy3 runtime
ARG TARGETPLATFORM
RUN --mount=type=bind,from=builder-pypy,source=/tmp,target=/tmp/ \
    TARGETPYPY=$( \
        case ${TARGETPLATFORM} in \
            linux/amd64 ) echo "linux64";; \
            linux/arm64 ) echo "aarch64";; \
        esac \
    ) \
    # && ls -l \
    && cp -r /tmp/pypy${AC_PYPY_VERSION}-${TARGETPYPY}/bin/* /usr/local/bin \
    && cp -r /tmp/pypy${AC_PYPY_VERSION}-${TARGETPYPY}/lib/* /usr/local/lib \
    && cp -r /tmp/pypy${AC_PYPY_VERSION}-${TARGETPYPY}/include/* /usr/local/include \
    && ln -s /usr/local/pypy${AC_PYPY_VERSION}-${TARGETPYPY}/bin/pypy3 /usr/local/bin/pypy3 \
    && ln -s /usr/local/pypy${AC_PYPY_VERSION}-${TARGETPYPY}/bin/pypy /usr/local/bin/pypy \
    && ln -s /usr/local/python3.13 /usr/local/python \
    && ln -s /usr/local/python3.13 /usr/local/python3 \

# # For cppyy with MacM1
# # cppyy-backend https://github.com/wlav/cppyy-backend/blob/master/cling/python/cppyy_backend/loader.py
# # when CURRENT_ARGS += ' -O2 -march=native' selected, import fails
# ENV EXTRA_CLING_ARGS=' -O2'

# Install some required packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        # required cppyy
        g++ \
        # required numpy, scipy, etc
#        libopenblas-dev \
        # required shapely
#        libgeos-dev \
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
# https://askubuntu.com/questions/1513927/ubuntu-24-04-docker-images-now-includes-user-ubuntu-with-uid-gid-1000
ARG USER_UID=1001
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
# wheelだとconflict多すぎてinstallしてpackageを移すほうがよさそう
# ENV PATH=$PATH:/home/$USERNAME/.local/bin
# RUN --mount=type=bind,from=builder-python,source=/tmp/wheels,target=/tmp/wheels/python \
#     --mount=type=bind,from=builder-pypy,source=/tmp/wheels,target=/tmp/wheels/pypy \
#     python -m pip install --no-index --no-deps /tmp/wheels/python/*.whl --no-cache --user\
#     && pypy -m pip install --no-index --no-deps /tmp/wheels/pypy/*.whl --no-cache --no-warn-script-location --user

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
