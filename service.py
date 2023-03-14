# _*_ coding: utf-8 _*_
import os

from eth_challenge_base.app import app

if __name__ == '__main__':
    os.environ["WEB3_PROVIDER_URI"] = "http://127.0.0.1:18545/"
    app.run(host='0.0.0.0', port=18080, debug=False)
