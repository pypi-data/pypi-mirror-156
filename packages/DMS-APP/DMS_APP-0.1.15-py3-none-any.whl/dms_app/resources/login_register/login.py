import hashlib
import logging
from flask import request, jsonify
from ...db.db_connection import database_access
from flask_restx import Resource, fields, reqparse
from ...namespace import api
from ...response_helper import get_response
import json
from bson import json_util
import smtplib
import re
from bson.objectid import ObjectId
from random import *
import random
import math
# from flask_jwt_extended import create_access_token, jwt_required


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

delete_user = api.model("DeleteUser", {
    "object_id": fields.String
})

user = reqparse.RequestParser()
user.add_argument("role", type=str, help="role")
user.add_argument("email", type=str, help="Email")
user.add_argument("page_no", type=int, required=True, help="Page number")
user.add_argument("page_limit", type=int, required=True, help="limit ")


class AddUser(Resource):
    @api.expect(user)
    def get(self):
        try:
            database_connection = database_access()
            dms_user_col = database_connection["dms_user"]
            args = user.parse_args()
            if args["role"] and args["email"]:
                data = dms_user_col.find(
                    {"role": args["role"], "$or": [{"email": {'$regex': '^{email}'.format(email=args["email"]),
                     '$options': 'mi'}}, {"first_name": {'$regex': '^{first_name}'.format(first_name=args["email"]),
                                                         '$options': 'mi'}}]}, {"password": 0})
                count = dms_user_col.count_documents(
                    {"role": args["role"],
                     "$or": [{"email": {'$regex': '^{email}'.format(email=args["email"]), '$options': 'mi'}},
                             {"first_name": {'$regex': '^{first_name}'.format(first_name=args["email"]),
                                             '$options': 'mi'}}]})
                total_count = dms_user_col.count_documents({})
                if len(list(data)):
                    data1 = dms_user_col.find(
                        {"role": args["role"], "$or": [{"email": {'$regex': '^{email}'.format(email=args["email"]),
                         '$options': 'mi'}}, {"first_name": {'$regex': '^{first_name}'.format(first_name=args["email"]),
                         '$options': 'mi'}}]}, {"password": 0}).skip(args["page_limit"] * (args["page_no"] - 1)).limit(
                        args["page_limit"])
                    data = list(data1)
                    logging.info(get_response(200))
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
            elif args["role"]:
                data = dms_user_col.find({"role": args["role"]})
                count = dms_user_col.count_documents({"role": args["role"]})
                total_count = dms_user_col.count_documents({})
                if len(list(data)):
                    data = dms_user_col.find({"role": args["role"]}, {"password": 0}).skip(
                        args["page_limit"] * (args["page_no"] - 1)).limit(
                        args["page_limit"])
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

            elif args["email"]:
                data = dms_user_col.find(
                    {"$or": [{"email": {'$regex': '^{email}'.format(email=args["email"]), '$options': 'mi'}},
                    {"first_name": {'$regex': '^{first_name}'.format(first_name=args["email"]), '$options': 'mi'}}]})
                count = dms_user_col.count_documents(
                    {"$or": [{"email": {'$regex': '^{email}'.format(email=args["email"]), '$options': 'mi'}},
                    {"first_name": {'$regex': '^{first_name}'.format(first_name=args["email"]), '$options': 'mi'}}]})
                total_count = dms_user_col.count_documents({})
                if len(list(data)):
                    data = dms_user_col.find(
                        {"$or": [{"email": {'$regex': '^{email}'.format(email=args["email"]), '$options': 'mi'}},
                                 {"first_name": {'$regex': '^{first_name}'.format(first_name=args["email"]),
                                                 '$options': 'mi'}}]}).skip(args["page_limit"] * (args["page_no"] - 1)).\
                        limit(args["page_limit"])
                    data = data
                    logging.info(get_response(200))
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
                data = dms_user_col.find({}, {"password": 0})
                count = dms_user_col.count_documents({})
                if len(list(data)):
                    logging.info(get_response(200))
                    _response = get_response(200)
                    data = dms_user_col.find({}, {"password": 0}).skip(args["page_limit"] * (args["page_no"] - 1)).limit(
                        args["page_limit"])
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
    def post(self):
        try:
            args = request.get_json()
            database_connection = database_access()
            dms_user_col = database_connection["dms_user"]
            digits = [i for i in range(0, 10)]
            otp = ""
            for i in range(6):
                index = math.floor(random.random() * 10)
                otp += str(digits[index])
            recipient = args['email'].strip()
            body = "Hello " + args["first_name"] + " " + args["last_name"] + "," + \
                   "\r\nOne Time Password for Driver Management System Application : " + str(otp)
            hash_password = hashlib.md5(str(otp).encode("utf-8")).digest()
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            regx = re.compile(args["email"], re.IGNORECASE)
            if not dms_user_col.find_one({"email": {'$regex': regx}}):
                server.login("dmsbackend12@gmail.com", "Dms@1234")
                server.sendmail('dmsbackend12@gmail.com', recipient, body)
                dms_user_col.insert_one(
                    {"first_name": args["first_name"], "last_name": args["last_name"], "email": args["email"],
                     "password": hash_password, "role": args["role"], "contact": args["contact"]})
                logging.info(get_response(200))
                return get_response(200)
            else:
                logging.error(get_response(409))
                return get_response(409)
        except Exception as e:
            _response = get_response(404)
            _response['message'] = 'Failed to Store User'
            logging.error(e)
            return _response

    @api.expect(put_user, validate=True)
    def put(self):
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
                logging.info(get_response(200))
                return get_response(200)
            else:
                logging.error(get_response(404))
                return get_response(404)
        except Exception as e:
            _response = get_response(404)
            _response['message'] = 'Failed to Update User'
            logging.error(e)
            return _response

    @api.expect(delete_user, validate=True)
    def delete(self):
        args = request.get_json()
        try:
            database_connection = database_access()
            dms_user_col = database_connection["dms_user"]
            if dms_user_col.find_one({"_id": ObjectId(args["object_id"])}):
                dms_user_col.delete_one({"_id": ObjectId(args["object_id"])})
                logging.info(get_response(200))
                return get_response(200)
            else:
                logging.error(get_response(404))
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
            check_email = dms_user_col.find_one({"email": {'$regex': regx_email}})
            hash_password = hashlib.md5(args["password"].encode('utf-8')).digest()
            if check_email:
                logging.info(get_response(200))
                _response = get_response(200)
                _response["role"] = json.loads(json_util.dumps(check_email["role"]))
                _response["first_name"] = json.loads(json_util.dumps(check_email["first_name"]))
                _response["last_name"] = json.loads(json_util.dumps(check_email["last_name"]))
                if check_email["password"] == hash_password:
                    # access_token = create_access_token(identity=check_email['email'])# create jwt token
                    # _response["access_token"] = access_token
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
    @api.expect(change_user_password, validate=True)
    def put(self):
        args = request.get_json()
        try:
            database_connection = database_access()
            dms_user_col = database_connection["dms_user"]
            hash_password = hashlib.md5(args["password"].encode("utf-8")).digest()
            regx_email = re.compile(args["email"], re.IGNORECASE)
            if dms_user_col.find_one({"email": {'$regex': regx_email}}):
                dms_user_col.update_one({"email": args["email"]}, {'$set':
                                                                       {"password": hash_password}})
                logging.info(get_response(200))
                return get_response(200)
            else:
                logging.error(get_response(409))
                return get_response(409)
        except Exception as e:
            _response = get_response(404)
            _response['message'] = 'Failed to Update User'
            logging.error(e)
            return _response