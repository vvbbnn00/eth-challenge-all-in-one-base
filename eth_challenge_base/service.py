import json
import logging
import os
import secrets
from decimal import Decimal
from glob import glob
from typing import Dict

import pyseto
from eth_typing import ChecksumAddress
from eth_utils import units
from pyseto import Token

from eth_challenge_base.config import Config, parse_config
from eth_challenge_base.ethereum import Account, Contract
from eth_challenge_base.exceptions import ServiceError

AUTHORIZATION_KEY = "authorization"
TOKEN_KEY = pyseto.Key.new(
    version=4,
    purpose="local",
    key=os.getenv("TOKEN_SECRET", secrets.token_hex(32)),
)


class ChallengeService:
    def __init__(self, project_root: str, config: Config) -> None:
        self._config = config
        self._project_root = project_root
        artifact_path = os.path.join(self._project_root, "build", "contracts")
        with open(os.path.join(artifact_path, f"{self._config.contract}.json")) as fp:
            build_json = json.load(fp)
        self._contract: Contract = Contract(build_json["abi"], build_json["bytecode"])
        self._source_code: Dict[str, str] = self._load_challenge_source(artifact_path)
        self._token_key = TOKEN_KEY

    def GetChallengeInfo(self):
        return {
            'description': self._config.description,
            'show_source': self._config.show_source,
            'solved_event': self._config.solved_event,
        }

    def NewPlayground(self):
        account: Account = Account()
        token: str = pyseto.encode(
            self._token_key, payload=account.private_key, footer=self._config.contract
        ).decode("utf-8")

        try:
            constructor = self._config.constructor
            total_value: int = self._contract.deploy.estimate_total_value(
                constructor.value, constructor.gas_limit, constructor.args
            )
        except Exception as e:
            raise ServiceError(
                code=500,
                message=str(e),
            )

        ether_value: Decimal = Decimal(total_value) / units.units["ether"] + Decimal(
            "0.0005"
        )

        logging.info("Playground account %s was created", account.address)
        return {
            'address': account.address,
            'token': token,
            'value': float(round(ether_value, 3)),
        }

    def GetAccount(self, context):
        account: Account = self._recoverAcctFromCtx(context)
        contract_addr: str = account.get_deployment_address()
        return {
            'address': account.address,
            'contract': contract_addr if account.nonce > 0 else None,
        }

    def DeployContract(self, context):
        account: Account = self._recoverAcctFromCtx(context)
        if account.balance == 0:
            raise ServiceError(
                code=400,
                message=f"It seems that you haven't "
                        f"send test ether to {account.address}, "
                        f"please send some first",
            )
        if account.nonce > 0:
            raise ServiceError(
                code=400,
                message="Challenge contract has already been deployed",
            )
        contract_addr: str = account.get_deployment_address()
        try:
            constructor = self._config.constructor
            tx_hash: str = self._contract.deploy(
                account, constructor.value, constructor.gas_limit, constructor.args
            )
        except Exception as e:
            raise ServiceError(
                code=500,
                message=str(e),
            )

        logging.info(
            "Contract %s was deployed by %s. Transaction hash %s",
            contract_addr,
            account.address,
            tx_hash,
        )
        return {
            'address': contract_addr,
            'tx_hash': tx_hash,
        }

    def GetFlag(self, context):
        account: Account = self._recoverAcctFromCtx(context)
        nonce: int = account.nonce
        if nonce == 0:
            raise ServiceError(
                code=400,
                message="Challenge contract has not yet been deployed",
            )
        contract_addr: ChecksumAddress = account.get_deployment_address(nonce - 1)

        if self._config.solved_event:
            if not context.get("tx_hash"):
                raise ServiceError(
                    code=400,
                    message="tx_hash is required",
                )
            tx_hash = context.get("tx_hash").strip()
            if not (
                    len(tx_hash) == 66
                    and tx_hash.startswith("0x")
                    and all(c in "0123456789abcdef" for c in tx_hash[2:])
            ):
                raise ServiceError(
                    code=400,
                    message="Invalid tx_hash",
                )

            try:
                is_solved = self._contract.is_solved(
                    contract_addr, self._config.solved_event, tx_hash
                )
            except Exception as e:
                raise ServiceError(
                    code=400,
                    message=str(e),
                )
        else:
            is_solved = self._contract.is_solved(contract_addr)

        if not is_solved:
            raise ServiceError(
                code=400,
                message="It seems that you haven't solved this challenge~",
            )

        logging.info(
            "Flag was captured in contract %s deployed by %s",
            contract_addr,
            account.address,
        )

        flag = os.environ.get("FLAG", 'flag not found, please contact admin')
        return {
            'flag': flag,
        }

    def GetSourceCode(self):
        return {
            'source': self._source_code,
        }

    def _load_challenge_source(self, artifact_path) -> Dict[str, str]:
        source: Dict[str, str] = {}
        if not self._config.show_source:
            return source
        for path in glob(os.path.join(artifact_path, "*.json")):
            try:
                with open(path) as fp:
                    build_json = json.load(fp)
            except json.JSONDecodeError:
                continue
            else:
                source_path: str = build_json["sourcePath"]
                source[source_path] = build_json["source"]

        return source

    def _recoverAcctFromCtx(self, session) -> Account:
        token = session.get('token')
        if not token:
            raise ServiceError(
                code=401,
                message="token is required",
            )

        try:
            decoded_token: Token = pyseto.decode(self._token_key, token.strip())
        except Exception as e:
            raise ServiceError(
                code=401,
                message=str(e),
            )

        if self._config.contract != decoded_token.footer.decode("utf-8"):
            raise ServiceError(
                code=401,
                message="invalid token",
            )

        return Account(decoded_token.payload.decode("utf-8"))


def getService(project_root: str):
    config = parse_config(os.path.join(project_root, "challenge.yml"))
    service = ChallengeService(project_root, config)
    return service
