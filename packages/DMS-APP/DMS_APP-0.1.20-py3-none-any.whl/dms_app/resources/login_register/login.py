import hashlib
import logging
from flask import request, Flask
from ...db.db_connection import database_access
from flask_restx import Resource, fields, reqparse
from ...namespace import api
from ...response_helper import get_response
import json
from bson import json_util
import re
from bson.objectid import ObjectId
from random import *
import random
import math
import jwt
from ...config import Config
from datetime import datetime, timedelta
from functools import wraps
import emails

sec_key = Config.SEC_KEY
post_user = api.model("AddUser", {
    "first_name": fields.String,
    "last_name": fields.String,
    "email": fields.String,
    "role": fields.String,
    "contact": fields.String,
})

put_user = api.model("PutUser", {
    "first_name": fields.String,
    "last_name": fields.String,
    "email": fields.String,
    "role": fields.String,
    "contact": fields.String,
})

get_all_User = reqparse.RequestParser()
get_all_User.add_argument("page_no", type=int, required=True, help="Page number")
get_all_User.add_argument("page_limit", type=int, required=True, help="limit ")

change_user_password = api.model("ChangePassword", {
    "email": fields.String,
    "password": fields.String
})

delete_user = reqparse.RequestParser()
delete_user.add_argument("object_id", type=str, help="Object Id")

user = reqparse.RequestParser()
user.add_argument("role", type=str, help="role")
user.add_argument("email", type=str, help="Email")
user.add_argument("page_no", type=int, required=True, help="Page number")
user.add_argument("page_limit", type=int, required=True, help="limit ")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        args = request.get_json()
        database_connection = database_access()
        token_coll = database_connection["bearer_token"]
        header = request.headers
        email = args["email_id"]
        session_id = args["session_id"]
        access_token = header["Authorization"]
        if email and session_id and access_token:
            token = email + "_" + session_id + "_" + access_token
        data = token_coll.find_one({"access_token": token})
        if data:
            token_coll.delete_one({"access_token": token})
            return f(*args, **kwargs)
        else:
            _response = get_response(404)
            _response["message"] = "You are unauthorised"
            return _response
    return decorated


token_required_get_data = reqparse.RequestParser()
token_required_get_data.add_argument("email_id", type=str, help="Email")
token_required_get_data.add_argument("session_id", type=str, help="Session ID")


def token_required_get(f):
    @wraps(f)
    @api.expect(token_required_get_data)
    def decorated(*args, **kwargs):
        args = token_required_get_data.parse_args()
        database_connection = database_access()
        token_coll = database_connection["bearer_token"]
        header = request.headers
        email = args["email_id"]
        session_id = args["session_id"]
        access_token = header["Authorization"]
        token = email + "_" + session_id + "_" + access_token
        data = token_coll.find_one({"access_token": token})
        if data:
            token_coll.delete_one({"access_token": token})
            return f(*args, **kwargs)
        else:
            _response = get_response(404)
            _response["message"] = "You are unauthorised"
            return _response
    return decorated


class AddUser(Resource):
    @token_required_get
    @api.expect(user)
    def get(self, *args):
        try:
            database_connection = database_access()
            dms_user_col = database_connection["dms_user"]
            page_no = request.args.get("page_no")
            page_limit = request.args.get("page_limit")
            email = request.args.get("email")
            role = request.args.get("role")
            if role and email:
                data = list(dms_user_col.find(
                    {"role": role, "$or": [
                        {"email": {'$regex': '^{email}'.format(email=email), '$options': 'mi'}},
                        {"first_name": {'$regex': '^{first_name}'.format(first_name=email),
                         '$options': 'mi'}}]}, {"password": 0}).skip(int(page_limit) * (int(page_no) - 1)).limit(
                    int(page_limit)))
                count = dms_user_col.count_documents(
                    {"role": role,
                     "$or": [{"email": {'$regex': '^{email}'.format(email=email), '$options': 'mi'}},
                             {"first_name": {'$regex': '^{first_name}'.format(first_name=email),
                                             '$options': 'mi'}}]})
                total_count = dms_user_col.count_documents({})
                if len(data):
                    _response = get_response(200)
                    _response["data"] = json.loads(json_util.dumps(data))
                    _response["count"] = json.loads(json_util.dumps(count))
                    _response["total_count"] = json.loads(json_util.dumps(total_count))
                    return _response
                else:
                    _response = get_response(404)
                    _response["data"] = []
                    _response["count"] = 0
                    return _response
            elif role:
                data = list(dms_user_col.find({"role": role}, {"password": 0}).skip(int(page_limit) * (int(page_no) - 1)).limit(
                    int(page_limit)))
                count = dms_user_col.count_documents({"role": role})
                total_count = dms_user_col.count_documents({})
                if len(data):
                    _response = get_response(200)
                    _response["data"] = json.loads(json_util.dumps(data))
                    _response["count"] = json.loads(json_util.dumps(count))
                    _response["total_count"] = json.loads(json_util.dumps(total_count))
                    return _response
                else:
                    _response = get_response(404)
                    _response["data"] = []
                    _response["count"] = 0
                    return _response
            elif email:
                data = list(dms_user_col.find(
                    {"$or": [{"email": {'$regex': '^{email}'.format(email=email), '$options': 'mi'}},
                             {"first_name": {'$regex': '^{first_name}'.format(first_name=email),
                                             '$options': 'mi'}}]}).skip(int(page_limit) * (int(page_no) - 1)).limit(
                    int(page_limit)))
                count = dms_user_col.count_documents(
                    {"$or": [{"email": {'$regex': '^{email}'.format(email=email), '$options': 'mi'}},
                    {"first_name": {'$regex': '^{first_name}'.format(first_name=email), '$options': 'mi'}}]})
                total_count = dms_user_col.count_documents({})
                if len(data):
                    _response = get_response(200)
                    _response["data"] = json.loads(json_util.dumps(data))
                    _response["count"] = json.loads(json_util.dumps(count))
                    _response["total_count"] = json.loads(json_util.dumps(total_count))
                    return _response
                else:
                    _response = get_response(404)
                    _response["data"] = []
                    _response["count"] = 0
                    return _response
            else:
                data = list(dms_user_col.find({}, {"password": 0}).skip(int(page_limit) * (int(page_no) - 1)).limit(
                    int(page_limit)))
                count = dms_user_col.count_documents({})
                if len(data):
                    _response = get_response(200)
                    _response["data"] = json.loads(json_util.dumps(data))
                    _response["count"] = json.loads(json_util.dumps(count))
                    return _response
                else:
                    _response = get_response(404)
                    _response["data"] = []
                    _response["count"] = 0
                    return _response
        except Exception as e:
            _response = get_response(404)
            _response['message'] = 'User Not Found'
            logging.error(e)
            return _response

    @api.expect(post_user, validate=True)
    @token_required
    def post(self, *args):
        try:
            args = request.get_json()
            database_connection = database_access()
            dms_user_col = database_connection["dms_user"]
            digits = [i for i in range(0, 10)]
            otp = ""
            for i in range(6):
                index = math.floor(random.random() * 10)
                otp += str(digits[index])
            recipient = args["email"].strip()
            hash_password = hashlib.md5(str(otp).encode("utf-8")).digest()
            regx = re.compile(args["email"], re.IGNORECASE)
            if not dms_user_col.find_one({"email": {'$regex': regx}}):
                message = emails.html(
                    html="<p>Hello {first_name} {last_name},<br> One Time Password for Driver Management System "
                         "Application : <strong>{otp}</strong>  </p>".format(first_name=args["first_name"], last_name=args["last_name"], otp=str(otp)),
                    subject="One Time Password",
                    mail_from="notification@autoplant.systems",
                )
                message.send(
                    to=recipient,
                    smtp={
                        "host": "email-smtp.ap-south-1.amazonaws.com",
                        "port": 587,
                        "timeout": 10,
                        "user": "AKIAZGDBWNF3SRLJAHOB",
                        "password": "BGw2xVcL0CCqV1dOMI8QmrEKXLaL10c2cf/LffJFaxrH",
                        "tls": True,
                    },
                )

                dms_user_col.insert_one(
                    {"first_name": args["first_name"], "last_name": args["last_name"], "email": args["email"],
                     "password": hash_password, "role": args["role"], "contact": args["contact"]})
                return get_response(200)
            else:
                return get_response(409)
        except Exception as e:
            _response = get_response(404)
            _response['message'] = 'Failed to Store User'
            logging.error(e)
            return _response

    @token_required
    @api.expect(put_user, validate=True)
    def put(self, *args):
        args = request.get_json()
        try:
            database_connection = database_access()
            dms_user_col = database_connection["dms_user"]
            regx_email = re.compile(args["email"], re.IGNORECASE)
            if dms_user_col.find_one({"email": {'$regex': regx_email}}):
                dms_user_col.update_one({"email": args["email"]}, {
                    '$set':
                        {"first_name": args["first_name"], "last_name": args["last_name"], "email": args["email"],
                            "role": args["role"], "contact": args["contact"]}})
                return get_response(200)
            else:
                return get_response(404)
        except Exception as e:
            _response = get_response(404)
            _response['message'] = 'Failed to Update User'
            logging.error(e)
            return _response

    @token_required_get
    @api.expect(delete_user, validate=True)
    def delete(self, *args):
        args = delete_user.parse_args()
        try:
            database_connection = database_access()
            dms_user_col = database_connection["dms_user"]
            if dms_user_col.find_one({"_id": ObjectId(args["object_id"])}):
                dms_user_col.delete_one({"_id": ObjectId(args["object_id"])})
                return get_response(200)
            else:
                return get_response(404)
        except Exception as e:
            _response = get_response(404)
            _response['message'] = 'Failed to Delete User'
            logging.error(e)
            return _response


user_login = api.model("UserLogin", {
    "email": fields.String,
    "password": fields.String,
})


class Login(Resource):
    @api.expect(user_login, validate=True)
    def post(self):
        args = request.get_json()
        try:
            database_connection = database_access()
            dms_user_col = database_connection["dms_user"]
            regx_email = re.compile(args["email"], re.IGNORECASE)
            data = dms_user_col.find_one({"email": {'$regex': regx_email}})
            hash_password = hashlib.md5(args["password"].encode('utf-8')).digest()
            if data:
                _response = get_response(200)
                _response["role"] = json.loads(json_util.dumps(data["role"]))
                _response["first_name"] = json.loads(json_util.dumps(data["first_name"]))
                _response["last_name"] = json.loads(json_util.dumps(data["last_name"]))
                _response["email"] = json.loads(json_util.dumps(data["email"]))
                if data["password"] == hash_password:
                    session_id = jwt.encode({
                        'email': data['email'],
                        'exp': datetime.utcnow() + timedelta(days=1)
                    }, sec_key)
                    _response["session_id"] = session_id
                    if len(args["password"]) == 6 and args["password"].isdigit():
                        _response["otp"] = True
                        return _response
                    else:
                        _response["otp"] = False
                        return _response
                else:
                    logging.error(get_response(401))
                    return get_response(401)
            else:
                logging.error(get_response(404))
                return get_response(404)
        except Exception as e:
            _response = get_response(404)
            _response['message'] = 'Failed to Store User'
            logging.error(e)
            return _response


class ChangeUserPassword(Resource):
    @token_required
    @api.expect(change_user_password, validate=True)
    def put(self, *args):
        args = request.get_json()
        try:
            database_connection = database_access()
            dms_user_col = database_connection["dms_user"]
            hash_password = hashlib.md5(args["password"].encode("utf-8")).digest()
            regx_email = re.compile(args["email"], re.IGNORECASE)
            if dms_user_col.find_one({"email": {'$regex': regx_email}}):
                dms_user_col.update_one({"email": args["email"]}, {'$set': {"password": hash_password}})
                return get_response(200)
            else:
                logging.error(get_response(409))
                return get_response(409)
        except Exception as e:
            _response = get_response(404)
            _response['message'] = 'Failed to Update User'
            logging.error(e)
            return _response
