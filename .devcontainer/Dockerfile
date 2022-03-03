ARG VERSION=3.8.2
FROM python:${VERSION}

#Timezone Setting for Debian GNU/Linux 10
ENV TZ=Asia/Tokyo
RUN echo $TZ > /etc/timezone

#https://qiita.com/udzura/items/576c2c782adb241070bc
ENV DEBIAN_FRONTEND=noninteractive

# Working directory for 'RUN', 'CMD', 'ENTRYPOINT, 'COPY', 'ADD'
# https://docs.docker.jp/engine/reference/builder.html#workdir
ARG WORKDIR=/project
WORKDIR ${WORKDIR}

# Increase timeout for apt-get to 300 seconds
RUN /bin/echo -e "\n\
    Acquire::http::Timeout \"300\";\n\
    Acquire::ftp::Timeout \"300\";" >> /etc/apt/apt.conf.d/99timeout

# Configure apt and install packages
# pypy3 is installed as 7.0.0, but in AtCoder it should be 7.3.0.
RUN apt-get update \
    && apt-get -y --no-install-recommends install sudo vim zsh git ssh time tzdata tree sed pypy3\
    && curl -sL https://deb.nodesource.com/setup_14.x | bash - \
    && apt-get -y install nodejs\
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# change default shell
RUN zsh
ENV SHELL=/usr/bin/zsh
# Later, add to install zsh-completion, 

# Create a non-root user to use if preferred - see https://aka.ms/vscode-remote/containers/non-root-user.
# https://unit42.paloaltonetworks.jp/non-root-containers-kubernetes-cve-2019-11245-care/
# https://qiita.com/syoyo/items/6fa6597b7a6625000e33
ARG USERNAME=vscode
ARG USERPASSWD=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
# Add sudo support for non-root user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && RUN echo "$USERNAME:$USERPASSWD" | chpasswd

# copy requirements files
COPY ./requirements.txt /tmp/requirements.txt

# library install for atcoder
RUN pip install -r /tmp/requirements.txt\
    && npm install --global atcoder-cli@2.2.0

USER $USERNAME
