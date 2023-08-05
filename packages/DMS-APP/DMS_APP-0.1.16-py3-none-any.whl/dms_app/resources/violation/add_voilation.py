from flask import request
from flask_restx import Resource, fields, reqparse
from ...db.db_connection import database_access
from ...namespace import api
from ...response_helper import get_response
import logging
import json
from bson import json_util
from bson.objectid import ObjectId
# from flask_jwt_extended import jwt_required


resource_fields = api.model("ViolationAdd", {
    "violation_name": fields.String,
    "violation_desc": fields.String,
    "violation_type": fields.String,
    "date_added": fields.String,
    "added_by": fields.String,
    "status": fields.String,
})

resource_fields3 = api.model("ViolationUpdate", {
    "violation_id": fields.String,
    "violation_name": fields.String,
    "violation_desc": fields.String,
    "violation_type": fields.String,
    "date_added": fields.String,
    "added_by": fields.String,
    "status": fields.String,
})
resource_fields1 = api.model("ViolationUpdate", {
    "violation_id": fields.String,
    "status": fields.String,
})

get_all_Violations = reqparse.RequestParser()
get_all_Violations.add_argument("page_no", type=int, required=True, help="Page number")
get_all_Violations.add_argument("page_limit", type=int, required=True, help="limit ")
get_all_Violations.add_argument("violation_name", type=str, help="Violation Name")
get_all_Violations.add_argument("status", type=str, help="Status")

delete_Violation = reqparse.RequestParser()
delete_Violation.add_argument("violation_id", type=str, required=True, help="Violation ID")


class ViolationOperations(Resource):
    # @jwt_required()
    @api.expect(get_all_Violations)
    def get(self):
        try:
            args = get_all_Violations.parse_args()
            database_connection = database_access()
            violation_collection = database_connection["dms_violation"]
            regx = args["violation_name"]
            if args["status"] and args["violation_name"]:
                violations1 = violation_collection.find(
                    {"violation_name": {'$regex': '^{violation_name}'.format(violation_name=regx), '$options': 'mi'},
                     "status": args["status"]})
                count = violation_collection.count_documents(
                    {"violation_name": {'$regex': '^{violation_name}'.format(violation_name=regx), '$options': 'mi'},
                     "status": args["status"]})
                if len([violations1]):
                    violations = violation_collection.find(
                        {"violation_name": {'$regex': '^{violation_name}'.format(violation_name=regx),
                                            '$options': 'mi'}, "status": args["status"]}).skip(args["page_limit"] *
                                                                                               (args["page_no"] - 1)).limit(
                        args["page_limit"])
                    _response = get_response(200)
                    _response["data"] = json.loads(json_util.dumps(violations))
                    _response["count"] = json.loads(json_util.dumps(count))
                    return _response
                else:
                    _response = get_response(404)
                    _response["data"] = []
                    _response["count"] = 0
                    return _response

            elif args["status"]:
                violations = violation_collection.find({"status": args["status"]})
                count = violation_collection.count_documents({"status": args["status"]})
                if len(list(violations)):
                    violations = violation_collection.find(
                        {"status": args["status"]}).skip(args["page_limit"] * (args["page_no"] - 1)).limit(
                        args["page_limit"])
                    _response = get_response(200)
                    _response["data"] = json.loads(json_util.dumps(violations))
                    _response["count"] = json.loads(json_util.dumps(count))
                    return _response
                else:
                    _response = get_response(404)
                    _response["data"] = []
                    _response["count"] = 0
                    return _response
            elif args["violation_name"]:
                violations1 = violation_collection.find(
                    {"violation_name": {'$regex': '^{violation_name}'.format(violation_name=regx), '$options': 'mi'}})
                count = violation_collection.count_documents(
                    {"violation_name": {'$regex': '^{violation_name}'.format(violation_name=regx), '$options': 'mi'}})
                if len([violations1]):
                    violations = violation_collection.find(
                        {"violation_name": {'$regex': '^{violation_name}'.format(violation_name=regx), '$options': 'mi'}}). \
                        skip(args["page_limit"] * (args["page_no"] - 1)).limit(args["page_limit"])
                    _response = get_response(200)
                    _response["data"] = json.loads(json_util.dumps(violations))
                    _response["count"] = json.loads(json_util.dumps(count))
                    return _response
                else:
                    _response = get_response(404)
                    _response["data"] = []
                    _response["count"] = 0
                    return _response
            else:
                violations = violation_collection.find()
                count = violation_collection.count_documents({})
                if len(list(violations)):
                    violations = violation_collection.find().skip(args["page_limit"] * (args["page_no"] - 1)). \
                        limit(args["page_limit"])
                    _response = get_response(200)
                    _response["data"] = json.loads(json_util.dumps(violations))
                    _response["count"] = count
                    return _response
                else:
                    _response = get_response(404)
                    _response["data"] = []
                    _response["count"] = 0
                    return _response
        except Exception as e:
            _response = get_response(404)
            _response['message'] = 'Failed to Find Violation'
            logging.error(e)
            return _response

    # @jwt_required()
    @api.expect(resource_fields, validate=True)
    def post(self):
        args = request.get_json()
        try:
            database_connection = database_access()
            violation_collection = database_connection["dms_violation"]
            violation_collection.insert_one(args)
            logging.info(get_response(200))
            return get_response(200)
        except Exception as e:
            _response = get_response(404)
            _response['message'] = 'Failed to Store Violation'
            logging.error(e)
            return _response

    # @jwt_required()
    @api.expect(resource_fields1, validate=True)
    def put(self):
        args = request.get_json()
        try:
            database_connection = database_access()
            violation_collection = database_connection["dms_violation"]
            if violation_collection.find_one({"_id": ObjectId(args["violation_id"])}):
                violation_collection.update_one({"_id": ObjectId(args["violation_id"])}, {
                    '$set': {"status": args["status"]}})
                logging.info(get_response(200))
                return get_response(200)
            else:
                logging.error(get_response(404))
                return get_response(404)
        except Exception as e:
            _response = get_response(404)
            _response['message'] = 'Failed to Update Violation'
            logging.error(e)
            return _response

    # @jwt_required()
    @api.expect(delete_Violation, validate=True)
    def delete(self):
        try:
            database_connection = database_access()
            violation_collection = database_connection["dms_violation"]
            args = delete_Violation.parse_args()
            if violation_collection.find_one({"_id": ObjectId(args["violation_id"])}):
                violation_collection.delete_one({"_id": ObjectId(args["violation_id"])})
                logging.info(get_response(200))
                return get_response(200)
            else:
                logging.error(get_response(404))
                return get_response(404)
        except Exception as e:
            _response = get_response(404)
            _response['message'] = 'Failed to Delete Violation'
            logging.error(e)
            return _response


active_Violations = reqparse.RequestParser()
active_Violations.add_argument("page_no", type=int, required=True, help="Page number")
active_Violations.add_argument("page_limit", type=int, required=True, help="limit")


class ActiveViolations(Resource):
    # @jwt_required()
    @api.expect(active_Violations)
    def get(self):
        try:
            args = search_Violations.parse_args()
            database_connection = database_access()
            violation_collection = database_connection["dms_violation"]
            violations = violation_collection.find({"status": "active"})
            count = violation_collection.count_documents({"status": "active"})
            if len(list(violations)):
                violations = violation_collection.find(
                    {"status": "active"}).skip(args["page_limit"] * (args["page_no"] - 1)).limit(args["page_limit"])
                _response = get_response(200)
                _response["data"] = json.loads(json_util.dumps(violations))
                _response["count"] = json.loads(json_util.dumps(count))
                return _response
            else:
                return get_response(404)
        except Exception as e:
            _response = get_response(404)
            _response['message'] = 'Failed to Find Violation'
            logging.error(e)
            return _response


search_Violations = reqparse.RequestParser()
search_Violations.add_argument("violation_name", type=str, help="Violation Name")
search_Violations.add_argument("page_no", type=int, required=True, help="Page number")
search_Violations.add_argument("page_limit", type=int, required=True, help="limit")
search_Violations.add_argument("status", type=str, help="Status")


class SearchViolations(Resource):
    # @jwt_required()
    @api.expect(search_Violations)
    def get(self):
        try:
            args = search_Violations.parse_args()
            database_connection = database_access()
            violation_collection = database_connection["dms_violation"]
            regx = args["violation_name"]
            if args["status"] and args["violation_name"]:
                violations1 = violation_collection.find(
                    {"violation_name": {'$regex': '^{violation_name}'.format(violation_name=regx), '$options': 'mi'},
                     "status": args["status"]})
                count = violation_collection.count_documents(
                    {"violation_name": {'$regex': '^{violation_name}'.format(violation_name=regx), '$options': 'mi'},
                     "status": args["status"]})
                if len([violations1]):
                    violations = violation_collection.find(
                        {"violation_name": {'$regex': '^{violation_name}'.format(violation_name=regx),
                                            '$options': 'mi'}, "status": args["status"]}).skip(args["page_limit"] *
                                                                                               (args["page_no"] - 1)).limit(args["page_limit"])
                    _response = get_response(200)
                    _response["data"] = json.loads(json_util.dumps(violations))
                    _response["count"] = json.loads(json_util.dumps(count))
                    return _response
                else:
                    _response = get_response(404)
                    _response["data"] = []
                    _response["count"] = 0
                    return _response

            elif args["status"]:
                violations = violation_collection.find({"status": args["status"]})
                count = violation_collection.count_documents({"status": args["status"]})
                if len(list(violations)):
                    violations = violation_collection.find(
                        {"status": args["status"]}).skip(args["page_limit"] * (args["page_no"] - 1)).limit(args["page_limit"])
                    _response = get_response(200)
                    _response["data"] = json.loads(json_util.dumps(violations))
                    _response["count"] = json.loads(json_util.dumps(count))
                    return _response
                else:
                    _response = get_response(404)
                    _response["data"] = []
                    _response["count"] = 0
                    return _response

            else:
                violations1 = violation_collection.find(
                    {"violation_name": {'$regex': '^{violation_name}'.format(violation_name=regx), '$options': 'mi'}})
                count = violation_collection.count_documents(
                    {"violation_name": {'$regex': '^{violation_name}'.format(violation_name=regx), '$options': 'mi'}})
                if len([violations1]):
                    violations = violation_collection.find(
                        {"violation_name": {'$regex': '^{violation_name}'.format(violation_name=regx), '$options': 'mi'}}). \
                        skip(args["page_limit"] * (args["page_no"] - 1)).limit(args["page_limit"])
                    _response = get_response(200)
                    _response["data"] = json.loads(json_util.dumps(violations))
                    _response["count"] = json.loads(json_util.dumps(count))
                    return _response
                else:
                    _response = get_response(404)
                    _response["data"] = []
                    _response["count"] = 0
                    return _response
        except Exception as e:
            _response = get_response(404)
            _response['message'] = 'Failed to Find Violation'
            logging.error(e)
            return _response


class UpdateViolation(Resource):
    # @jwt_required()
    @api.expect(resource_fields3)
    def put(self):
        args = request.get_json()
        try:
            database_connection = database_access()
            violation_collection = database_connection["dms_violation"]
            if violation_collection.find_one({"_id": ObjectId(args["violation_id"])}):
                violation_collection.update_one({"_id": ObjectId(args["violation_id"])}, {
                    '$set': {"status": args["status"], "violation_name": args["violation_name"],
                             "violation_desc": args["violation_desc"], "violation_type": args["violation_type"],
                             "date_added": args["date_added"], "added_by": args["added_by"]}})
                logging.info(get_response(200))
                return get_response(200)
            else:
                logging.error(get_response(404))
                return get_response(404)
        except Exception as e:
            _response = get_response(404)
            _response['message'] = 'Failed to Update Violation'
            logging.error(e)
            return _response


violation_filter = reqparse.RequestParser()
violation_filter.add_argument("status", type=str, required=True, help="Status")
violation_filter.add_argument("page_no", type=int, required=True, help="Page number")
violation_filter.add_argument("page_limit", type=int, required=True, help="limit ")


class ViolationFilter(Resource):
    # @jwt_required()
    @api.expect(violation_filter)
    def get(self):
        try:
            database_connection = database_access()
            person_profile_col = database_connection["dms_violation"]
            args = violation_filter.parse_args()
            data = person_profile_col.find({"status": args['status']})
            count = person_profile_col.count_documents({"status": args['status']})
            if len(list(data)):
                data = person_profile_col.find({"status": args['status']}).skip(args["page_limit"] *(args["page_no"] - 1)).limit(args["page_limit"])
                _response = get_response(200)
                _response["data"] = json.loads(json_util.dumps(data))
                _response["count"] = json.loads(json_util.dumps(count))
                return _response
            else:
                return get_response(404)
        except Exception as e:
            _response = get_response(404)
            _response['message'] = 'Failed to Find Violation'
            logging.error(e)
            return _response
