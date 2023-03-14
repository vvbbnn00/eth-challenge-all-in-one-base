# _*_ coding: utf-8 _*_
import json


class ServiceError(Exception):
    def __init__(self, message: str, code: int = 500):
        self.message = message
        self.code = code

    def __str__(self):
        return json.dumps({
            'message': self.message,
            'code': self.code,
        })
