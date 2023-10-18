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
FROM ubuntu:22.04 as cert
WORKDIR /usr/share/ca-certificates/extra/
RUN --mount=type=bind,source=./certfiles,target=/usr/share/ca-certificates/extra/ \
    apt update && \
    apt-get install -y ca-certificates --no-install-recommends && \
    for f in $(ls *.pem); do \
        # update-ca-certificates will fail without this.
        # http://www.maibun.org/~nt/technicalnote/centos8/ssl4.html
        echo 'extra/'$f >> /etc/ca-certificates.conf ; \
    done && \
    update-ca-certificates

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
FROM ubuntu:22.04 as ac-img

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

# https://matsuand.github.io/docs.docker.jp.onthefly/engine/install/ubuntu/
RUN apt update \
    && apt install -y --no-install-recommends \
        # required from docker-cli
        curl \
        gnupg \
        lsb-release \
        # sudo \
        # required from atcoder-cli
        git \
        nodejs \
        # required from oh-my-posh installation
        # curl # (already required from docker) \
        unzip \
        # required my usage in container
        zsh \
        ssh \
    && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt update \
    && apt install -y docker-ce docker-ce-cli --no-install-recommends \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/* \
    && curl -kL https://bootstrap.pypa.io/get-pip.py | python3

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
ARG USER=vscode
ARG USERPASSWD=$USER
ARG USER_UID=1000
ARG USER_GID=$USER_UID
# ARG DOCKER_GID
RUN groupadd --gid $USER_GID $USER \
    && useradd --uid $USER_UID --gid $USER_GID -m $USER \
    && echo $USER:$USERPASSWD | chpasswd \
    # to modify gid of docker group in order to align with host setting 
    # If host's groupid of "docker" = 999, then you don't need to do 
    # && groupmod -g $DOCKER_GID docker
    && usermod -aG docker $USER
 
    # # Add sudo support for non-root user
    # && echo $USER ALL=\(ALL\) ALL >> /etc/sudoers.d/$USER \
    # && chmod 0440 /etc/sudoers.d/$USER

# Manage ownwership of directly which volumes will be mounted to
# # volume's owner which is created automatically by docker compose will be root
# # https://github.com/docker/compose/issues/3270#issuecomment-206214034
WORKDIR /home/$USER
RUN mkdir work \
    && chown $USER:$USER work

# Working directory for 'RUN', 'CMD', 'ENTRYPOINT, 'COPY', 'ADD'
# https://docs.docker.jp/engine/reference/builder.html#workdir
USER $USER

# Install and configure oj
ENV PATH=$PATH:/home/$USER/.local/lib/python3.10/site-packages:/home/$USER/.local/bin
RUN --mount=type=bind,source=./requirement,target=/tmp \
    python3 -m pip install --user --verbose -r /tmp/req_support_python.txt 

# COPY setting files from host
COPY --chown=$USER:$USER ./dotfiles/ /home/$USER/

# change default shell
ENV SHELL=/usr/bin/zsh

# Enable git configuration
ARG GITNAME
ARG GITEMAIL
RUN git config --global user.name $GITNAME \
    && git config --global user.email $GITEMAIL

WORKDIR /home/$USER/work
# CMD ["ssh","-o","StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null","-T","git@github.com"]
# CMD ["echo","'hello from ac-task"]