from enum import IntEnum
from flask import jsonify
class E_RC(IntEnum):
    RC_OK = 200
    RC_SUCCESS = 201
    RC_ERROR_DATABASE = 500
    RC_NOT_FOUND = 404
    RC_UNAUTHORIZED = 403
    RC_INVALID_INPUT = 422
    
class RC:
    """
    Return Code class to encapsulate return codes and their descriptions.
    """

    def __init__(self, code: int, description: str):
        self.code = code
        self.description = description

    def __str__(self):
        return f"{self.description}"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        return {
            "code": self.code,
            "description": self.description,
        }
    
    def is_ok(self):
        if self.code == E_RC.RC_OK or self.code == E_RC.RC_SUCCESS:
            return True
        else:
            return False
          
    def to_json(self):
        if self.is_ok():
            msg = "message"
        else:
            msg = "error"
            
        return jsonify({f"{msg}": self.description}), self.code
