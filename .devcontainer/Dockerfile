ARG VERSION=3.11.4
FROM python:${VERSION}-slim

#https://qiita.com/udzura/items/576c2c782adb241070bc
ENV DEBIAN_FRONTEND=noninteractive

# Increase timeout for apt-get to 300 seconds
RUN /bin/echo -e "\n\
    Acquire::http::Timeout \"300\";\n\
    Acquire::ftp::Timeout \"300\";" >> /etc/apt/apt.conf.d/99timeout

# Configure apt and install packages
# g++ needs following reason (fail to install cppyy with pip):
#   https://qiita.com/kai0706/items/d6ca791e9815d61d5132
RUN apt-get update \
    && apt-get -y --no-install-recommends install \
        sudo vim zsh time tzdata curl git ssh\
        wget bzip2 gcc g++ gfortran libopenblas-dev liblapack-dev pkg-config libgeos-dev \
        build-essential gdb lcov libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev \
        libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev \
        lzma lzma-dev tk-dev uuid-dev zlib1g-dev \
        # https://github.com/deepgully/pyzil/issues/6
        # https://devpress.csdn.net/k8s/62fceb917e66823466190f7a.html
        libgmp-dev libmpc-dev libmpfr-dev

# separate curl installation
# nodejs<=16 is not worked on WSL2 on Ubunts 20.04 (npm seems to be missing)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get -y install nodejs \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Pypy installation
# ref: https://zenn.dev/ytdrep/articles/d65c26201042eb
# https://downloads.python.org/pypy/
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
    && wget https://bootstrap.pypa.io/get-pip.py \
    && pypy3 get-pip.py --break-system-packages

# Timezone Setting for Debian GNU/Linux 10
# Ref: https://qiita.com/pyon_kiti_jp/items/e9235f9f49430bb845bb
ARG TZ
RUN ln -s -f /usr/share/zoneinfo/$TZ /etc/localtime 
RUN echo $TZ | tee /etc/timezone >/dev/null
ENV TZ=$TZ

# Create a non-root user to use if preferred - see https://aka.ms/vscode-remote/containers/non-root-user.
# https://unit42.paloaltonetworks.jp/non-root-containers-kubernetes-cve-2019-11245-care/
# https://qiita.com/syoyo/items/6fa6597b7a6625000e33
ARG USERNAME
ARG USERPASSWD
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME:$USERPASSWD | chpasswd \
# Add sudo support for non-root user
    && echo $USERNAME ALL=\(ALL\) ALL >> /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# # copy requirements files for pip and library install for atcoder
# COPY --chown=$USERNAME ./requirements.txt /tmp/requirements.txt
# RUN pip install -r /tmp/requirements.txt\
#     && npm install --global atcoder-cli@2.2.0

# Install for oh-my-posh
COPY --chown=$USERNAME ./dotfiles/.iterm2.omp.json /home/$USERNAME/
RUN wget https://github.com/JanDeDobbeleer/oh-my-posh/releases/latest/download/posh-linux-amd64 -O /usr/local/bin/oh-my-posh \
    && chmod +x /usr/local/bin/oh-my-posh

# install and configure for atcoder-cli
COPY --chown=$USERNAME:$USERNAME templates/atcoder-cli-nodejs/ /home/$USERNAME/.config/atcoder-cli-nodejs/
RUN npm install --global atcoder-cli@2.2.0 \
    && chown -R $USERNAME:$USERNAME /home/$USERNAME/.config/

# change default shell
USER $USERNAME
ENV SHELL=/usr/bin/zsh

# from here, python package installation
COPY --chown=$USERNAME ./requirement/*.txt /tmp/
RUN python -m pip install -U setuptools==66.0.0 \
    && python -m pip install cmake wheel \
    && python -m pip install -r /tmp/requirements_python.txt
RUN pypy3 -m pip install -r /tmp/requirements_pypy.txt

# Countermeasure for oj
# export PATH=$PATH:/home/$(whoami)/.local/bin
ENV PATH=$PATH:/home/$USERNAME/.local/bin

# Working directory for 'RUN', 'CMD', 'ENTRYPOINT, 'COPY', 'ADD'
# https://docs.docker.jp/engine/reference/builder.html#workdir
WORKDIR /home/$USERNAME

# COPY setting files from host
COPY --chown=$USERNAME ./dotfiles/.zshrc /home/$USERNAME/

# Enable atcoder-cli configuration
RUN acc config default-template py \
    && acc config default-task-choice all \
    && acc config default-test-dirname-format test \
    && acc config oj-path /home/$(whoami)/.local/bin/oj

# Enable git configuration
ARG GITNAME
ARG GITEMAIL
RUN git config --global user.name $GITNAME \
    && git config --global user.email $GITEMAIL
