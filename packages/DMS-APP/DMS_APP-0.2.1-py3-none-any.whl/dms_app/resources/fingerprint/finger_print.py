from flask import request
from flask_restx import Resource, fields, reqparse
from ...db.db_connection import database_access
from ...namespace import api
from ...response_helper import get_response
import base64
import cv2
import os
import logging
from ..login_register.login import token_required

createFingerPrint = api.model("CreateFingerprint", {
    "person_id": fields.String,
    "base64": fields.Raw([])
})

fingerPrintDelete = api.model("fingerPrintDelete", {
    "person_id": fields.String
})

matchFingerPrint = api.model("matchFingerprint", {
    "base64": fields.Raw([])
})


class AddFingerprint(Resource):
    @token_required
    @api.expect(createFingerPrint)
    def post(self, *args):
        args = request.get_json()
        person_id = args['person_id']
        images_coll = args['base64']
        database_connection = database_access()
        person_profile_col = database_connection["person_profile"]
        data = person_profile_col.find_one({'person.person_id': person_id})
        if data is not None:
            _response = get_response(404)
            _response['message'] = "Person id already exists"
            logging.error(_response)
            return _response
        for i in range(0, len(images_coll)):
            try:
                image_binary = base64.decodebytes(bytes(images_coll[i], 'utf-8'))
                path = os.getenv('fingerprint_Path')
                with open(path + "/" + str(person_id) + "_" + str(i + 1) + "" + ".jpeg", 'wb') as f:
                    f.write(image_binary)
            except Exception:
                _response = get_response(404)
                _response['message'] = 'Unable to save file'
                logging.error(_response)
        logging.info(get_response(200))
        return get_response(200)



class MatchFingerprint(Resource):
    @token_required
    @api.expect(matchFingerPrint)
    def post(self, *args):
        args = request.get_json()
        images_coll = args['base64'][0]['base64str1']
        image_binary = base64.decodebytes(bytes(images_coll, 'utf-8'))
        path = os.getenv('fingerprint_Path')
        sample_path = os.getenv('fingerprint_sample')
        with open(sample_path+"\sample.jpeg", 'wb') as f:
            f.write(image_binary)
        test_original = cv2.imread(sample_path+"\sample.jpeg")
        match_list = []
        file_list = []
        for file in [file for file in os.listdir(path)]:
            file_list.append(file)
            _image = cv2.imread(path + '/' + file)
            detector = cv2.SIFT_create()
            keypoints1, descriptors1 = detector.detectAndCompute(test_original, None)
            keypoints2, descriptors2 = detector.detectAndCompute(_image, None)
            matcher = cv2.DescriptorMatcher_create(cv2.DescriptorMatcher_FLANNBASED)
            knn_matches = matcher.knnMatch(descriptors1, descriptors2, 2)
            ratio_thresh = 0.7
            good_matches = []
            lenth_match = []
            for m, n in knn_matches:
                if m.distance < ratio_thresh * n.distance:
                    good_matches.append(m)
            match_list.append(len(good_matches))
            if len(good_matches) > 100:
                _response = get_response(200)
                _response['person_id'] = file.split('_')[0:1]
                logging.info(get_response(200))
                return _response
        if max(match_list) > 50: 
            var = file_list[match_list.index(max(match_list))]
            _response = get_response(200)
            _response['person_id'] = var.split('_')[0:1]
            logging.info(get_response(200))
            return _response
        else:
            _response = get_response(404)
            _response['message'] = "No Match Found"
            logging.error(_response)
            return _response