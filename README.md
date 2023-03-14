# eth-challenge-base

![Docker size](https://badgen.net/docker/size/vvbbnn00/eth-challenge-all-in-one-base/beta?color=cyan)
![License: MIT](https://badgen.net/github/license/vvbbnn00/eth-challenge-all-in-one-base?color=yellow)

An all-in-one web docker for building ethereum contract challenges in capture the flag (CTF).

## Getting Started

### Quick Demo

Use the following command to run a quick demo:

```bash
docker run -it -p 20000:80 -e FLAG=slctf{flag} vvbbnn00/eth-challenge-all-in-one:beta
```

Then you can access the challenge at `http://localhost:20000/challenge`.

To get eth from faucet, you can visit `http://localhost:20000/`.

The JSON RPC API is available at `http://localhost:20000/jsonrpc`.

**Mention that the api is not compatible with Remix!**

## Usage

### Create challenge project based on [example-deployment](https://github.com/vvbbnn00/eth-challenge-all-in-one-base/tree/main/example-deployment)

The `build.py` script will compile the contracts and generate the challenge for you.
Before building the image, please run it first.

```shell
python build.py
```

If you miss the requirements, you can install them by running:

```shell
pip install -r requirements.txt
```

 In the `challenge` dictionary, you can modify the challenges.

* The `contracts` directory is where you should code the challenge contract, specifically, you need to implement [isSolved()](https://github.com/chainflag/eth-challenge-base/blob/main/example/contracts/Example.sol#L18) function to check if it is solved.
* The `challenge.yml` file is the config for specifying challenge description, flag, contract name, constructor, gas limit etc. Refer to the comments in this file for more details.

>You can build multi-contract challenges by deploying contracts in a setup contract's constructor

### Build your challenge docker

Use the following command to build a docker image:

```bash
cd example-deployment/
docker image build -t <your-challenge-name> .
```

Then you can run the docker image:

```bash
docker run -p port:80 --env FLAG=<your-flag> <your-challenge-name>
```


## Acknowledgements
Many thanks to [JetBrains](https://jb.gg/OpenSourceSupport) for providing their excellent tools and an open source license to support the development of this project.

This project is developed based on [eth-challenge-base](https://github.com/chainflag/eth-challenge-base), thanks a lot.

## License

Distributed under the MIT License. See LICENSE for more information.
