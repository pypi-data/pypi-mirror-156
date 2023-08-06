from flask import request
from flask_restx import Resource, fields, reqparse
from ...db.db_connection import database_access
from ...namespace import api
from ...response_helper import get_response
import base64
import cv2
import os
# from flask_jwt_extended import jwt_required


ccFingerPrint = api.model("CFingerprint", {
    "person_id": fields.String,
    "base64": fields.Raw([])
})

fingerPrintDelete = api.model("fingerPrintDelete", {
    "person_id": fields.String
})

mFingerPrint = api.model("mFingerprint", {
    "base64": fields.Raw([])
})


class AddFingerprint(Resource):
    # @jwt_required()
    @api.expect(ccFingerPrint)
    def post(self):
        args = request.get_json()
        person_id = args['person_id']
        imeges_coll = args['base64']
        database_connection = database_access()
        person_profile_col = database_connection["person_profile"]
        data = person_profile_col.find_one({'person.person_id': person_id})
        if data is not None:
            _response = get_response(404)
            _response['message'] = "Person id already exists"
            return _response

        for i in range(0, len(imeges_coll)):
            try:
                image_binary = base64.decodebytes(bytes(imeges_coll[i], 'utf-8'))
                path = os.getenv('fingerprint_Path')
                with open(path + "/" + str(person_id) + "_" + str(i + 1) + "_" + ".tif", 'wb') as f:
                    f.write(image_binary)
            except Exception:
                _response = get_response(404)
                _response['message'] = 'Unable to save file'
        return get_response(200)


class MatchFingerprint(Resource):
    # @jwt_required()
    @api.expect(mFingerPrint)
    def post(self):
        args = request.get_json()
        for i in range(len(args["base64"])):
            imeges_coll = args['base64'][0]['base64str1']

            image_binary = base64.decodebytes(bytes(imeges_coll, 'utf-8'))
            path = os.getenv('fingerprint_Path')
            sample_path = os.getenv('fingerprint_sample')
            with open(sample_path+"/sample.tif", 'wb') as f:
                f.write(image_binary)

            test_original = cv2.imread(sample_path+"/sample.tif")

            for file in [file for file in os.listdir(path)]:
                _image = cv2.imread(path + '/' + file)

                detector = cv2.SIFT_create()
                keypoints1, descriptors1 = detector.detectAndCompute(test_original, None)
                keypoints2, descriptors2 = detector.detectAndCompute(_image, None)

                matcher = cv2.DescriptorMatcher_create(cv2.DescriptorMatcher_FLANNBASED)
                knn_matches = matcher.knnMatch(descriptors1, descriptors2, 2)

                ratio_thresh = 0.7
                good_matches = []
                for m, n in knn_matches:
                    if m.distance < ratio_thresh * n.distance:
                        good_matches.append(m)
                print(len(good_matches), file)
                if len(good_matches) > 100:
                    _response = get_response(200)
                    _response["person_id"] = file.split('_')[0:1]
                    return _response

            else:
                _response = get_response(404)
                _response['message'] = "No Match Found"
                return _response
