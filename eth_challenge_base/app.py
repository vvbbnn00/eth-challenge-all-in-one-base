import os
import secrets
from flask import *

from eth_challenge_base.exceptions import ServiceError
from eth_challenge_base.service import getService

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", secrets.token_hex(32))

# os.environ['DEBUG_MODE'] = 'True'

if os.environ.get("DEBUG_MODE", False):
    project_root = os.getcwd()
    project_root = os.path.join(project_root, "../challenge")
else:
    project_root = os.environ.get("PROJECT_ROOT", None)
service = getService(project_root)


@app.errorhandler(ServiceError)
def handle_service_error(e):
    resp = make_response(str(e), 200)
    resp.headers["Content-Type"] = "application/json"
    return resp


@app.route("/")
def index():
    # Get challenge info
    challenge_info = service.GetChallengeInfo()
    if challenge_info is None:
        return {
            "message": "Challenge not found, please contact the admin",
            "code": 404,
        }, 200
    # {'description': '', 'show_source': True, 'solved_event': ''}
    source_code = None
    if challenge_info.get('show_source', True):
        source = service.GetSourceCode()
        source = source.get('source', None)
        source_code = ''
        for k, v in source.items():
            source_code += f'// File: {k} \n\n{v}\n'
    return render_template(
        "index.html",
        challenge_info=challenge_info,
        source_code=source_code,
    )


@app.route("/create", methods=["POST"])
def create_playground():
    # Create playground account
    playground = service.NewPlayground()
    if playground is None:
        return {
            "message": "Failed to create playground",
            "code": 500,
        }, 200
    return {
        "code": 200,
        "address": playground["address"],
        "token": playground["token"]
    }


@app.route("/account", methods=["POST"])
def get_account():
    account = service.GetAccount(request.form)
    if account is None:
        return {
            "message": "Failed to get account",
            "code": 500,
        }, 200
    return {
        "code": 200,
        "address": account["address"],
        "contract": account["contract"],
    }


@app.route("/deploy", methods=["POST"])
def deploy_contract():
    # Deploy contract
    contract = service.DeployContract(request.form)
    if contract is None:
        return {
            "message": "Failed to deploy contract",
            "code": 500,
        }, 200
    address = contract["address"]
    tx_hash = contract["tx_hash"]
    return {
        "code": 200,
        "address": address,
        "tx_hash": tx_hash,
    }


@app.route("/flag", methods=["POST"])
def get_flag():
    # Get flag
    flag = service.GetFlag(request.form)
    if flag is None:
        return {
            "message": "Failed to get flag, please contact admin",
            "code": 500,
        }, 200
    return {
        "code": 200,
        "flag": flag["flag"],
    }


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=18081, debug=False)
