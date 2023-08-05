import logging
from flask import Flask, session, request
from ...db.db_connection import database_access
from flask_restx import Resource
from ...response_helper import get_response
import jwt
from datetime import datetime, timedelta
from dms_app.config import Config
from flask_cors import cross_origin

sec_key = Config.SEC_KEY
print(sec_key)


class CreateToken(Resource):
	@cross_origin(supports_credentials=True)
	def post(self, *args):
		try:
			database_connection = database_access()
			token_coll = database_connection["bearer_token"]
			session_id = session.get("session_id")
			email = session.get("email")
			print(dir(request))
			print(request.headers)
			print(session)
			if session_id:
				token = jwt.encode({
					'session_id': session_id, 'email': email,
					'exp': datetime.utcnow() + timedelta(minutes=30)
				}, sec_key)
				_response = get_response(200)
				_response["access_token"] = "bearer" + " " + token
				access_token = email + "_" + session_id + "_" + "bearer"+" "+token
				token_coll.insert_one({"access_token": access_token})
				return _response
			else:
				_response = get_response(404)
				_response["message"] = "session id expired"
				return _response
		except Exception as e:
			_response = get_response(404)
			_response['message'] = 'Failed to Store User'
			logging.error(e)
			return _response
