FROM --platform=linux/amd64 ethereum/client-go:v1.11.4 as geth
FROM --platform=linux/amd64 chainflag/eth-faucet:1.1.0 as eth-faucet
FROM --platform=linux/amd64 python:3.9-slim-buster

WORKDIR /home/ctf

# apt change source to ustc
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list \
    && sed -i 's/security.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list

# Install build-essential wget
RUN apt update \
    && apt install -y --no-install-recommends build-essential wget musl-dev gnupg

# add nginx http://nginx.org/packages/mainline/debian/dists/buster/
RUN echo "deb http://nginx.org/packages/mainline/debian/ buster nginx" >> /etc/apt/sources.list \
    && echo "deb-src http://nginx.org/packages/mainline/debian/ buster nginx" >> /etc/apt/sources.list \
    && wget http://nginx.org/keys/nginx_signing.key \
    && apt-key add nginx_signing.key \
    && rm nginx_signing.key

# Install build-essential
RUN apt update \
    && apt install -y --no-install-recommends nginx nginx-module-njs \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Get geth from the official repo
COPY --from=geth /usr/local/bin/geth /usr/local/bin/

# Get chainflag/eth-faucet:1.1.0 from the official repo
COPY --from=eth-faucet /app/eth-faucet /usr/local/bin/

# geth config
COPY geth/proxy/eth-jsonrpc-access.js /etc/nginx
COPY geth/proxy/nginx.conf /etc/nginx
COPY geth/genesis.json.template /genesis.json.template

# challenge config
COPY challenge /home/ctf/challenge
COPY eth_challenge_base eth_challenge_base
COPY service.py .

# entrypoint
COPY entrypoint.sh /entrypoint.sh
COPY eth-faucet.sh /eth-faucet.sh
RUN mkdir /var/log/ctf
RUN chmod +x /entrypoint.sh && \
    chmod +x /eth-faucet.sh

ENV PROJECT_ROOT /home/ctf/challenge

EXPOSE 80

ENTRYPOINT ["sh"]
CMD ["/entrypoint.sh"]
