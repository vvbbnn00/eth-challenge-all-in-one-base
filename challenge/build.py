# _*_ coding: utf-8 _*_
import os

from brownie import project
from solcx import install

default = os.getenv(
    "SOLC_DOWNLOAD_BASE", "https://cdn.jsdelivr.net/gh/ethereum/solc-bin@latest"
).rstrip("/")
install.BINARY_DOWNLOAD_BASE = "https://github.com/ethereum/solc-bin/blob/gh-pages/{}-amd64/{}?raw=true"
project.load(".")