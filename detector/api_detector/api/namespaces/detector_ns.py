from flask_restx import Resource
from flask import Response, jsonify
import threading

from api_detector import logger
from api_detector.api.v1 import api
from api_detector.utils import handle500error

from api_detector.api.parsers.detector_parsers import matrices_parser
from api_detector.models.manager import DetectorManager

model = DetectorManager()

detector_ns = api.namespace('detector', description='Detector operations')

@detector_ns.route('/detect_seism')
class ExampleDetectionData(Resource):
    """
    Example generation operations
    """
    @api.response(200, 'Example successful')
    @api.response(400, 'Invalid input')
    @api.response(404, 'LLM not found')
    @api.response(500, 'Unknown error')
    def post(self):
        try:
            args = matrices_parser.parse_args()
            task_thread = threading.Thread(target=model.start_detection, args=(args['matrices'],))
            task_thread.start()
            return jsonify({"message": "Detection started"})
        except Exception as e:
            return handle500error(detector_ns, str(e))

