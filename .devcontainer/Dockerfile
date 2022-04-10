ARG VERSION=3.8.2
FROM python:${VERSION}

# Setting account name for AtCoder and github
ENV ACUSER=forzaMilan
ENV REMOTE=git@github.com:21kazu13/AtCoder.git

#Timezone Setting for Debian GNU/Linux 10
ENV TZ=Asia/Tokyo
RUN echo $TZ > /etc/timezone

#https://qiita.com/udzura/items/576c2c782adb241070bc
ENV DEBIAN_FRONTEND=noninteractive

# Working directory for 'RUN', 'CMD', 'ENTRYPOINT, 'COPY', 'ADD'
# https://docs.docker.jp/engine/reference/builder.html#workdir
# ARG WORKDIR=/project
# WORKDIR $WORKDIR

# Increase timeout for apt-get to 300 seconds
RUN /bin/echo -e "\n\
    Acquire::http::Timeout \"300\";\n\
    Acquire::ftp::Timeout \"300\";" >> /etc/apt/apt.conf.d/99timeout

# Configure apt and install packages
# pypy3 is installed as 7.0.0, but in AtCoder it should be 7.3.0.
RUN apt-get update \
    && apt-get -y --no-install-recommends install sudo vim zsh time tzdata pypy3\
    && curl -sL https://deb.nodesource.com/setup_14.x | bash - \
    && apt-get -y install nodejs \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

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

# copy requirements files for pip and library install for atcoder
COPY --chown=$USERNAME ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt\
    && npm install --global atcoder-cli@2.2.0

# Install for oh-my-posh
COPY --chown=$USERNAME ./dotfiles/.iterm2.omp.json /home/$USERNAME/
RUN wget https://github.com/JanDeDobbeleer/oh-my-posh/releases/latest/download/posh-linux-amd64 -O /usr/local/bin/oh-my-posh \
    && chmod +x /usr/local/bin/oh-my-posh
    
# configure for atcoder-cli and online-judge-tools
COPY --chown=$USERNAME:$USERNAME templates/ /home/$USERNAME/.config/atcoder-cli-nodejs/
RUN chown -R $USERNAME:$USERNAME /home/$USERNAME/.config/

# change default shell
USER $USERNAME
ENV SHELL=/usr/bin/zsh

# COPY setting files from host
COPY --chown=$USERNAME ./dotfiles/.zshrc /home/$USERNAME/

# Enable atcoder-cli configuration
RUN acc config default-template py \
    && acc config default-task-choice all \
    && acc config default-test-dirname-format test

WORKDIR /home/$USERNAME

# docker-compose is not support for docker BuildKit??
# RUN --mount=type=ssh git clone --depth 1 git@github.com:21kazu13/AtCoder.git