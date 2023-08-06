from flask import session
from flask_restx import Resource
from ...response_helper import get_response


class Logout(Resource):
    def post(self):
        session["email"] = None
        session["session_id"] = None
        _response = get_response(200)
        return _response