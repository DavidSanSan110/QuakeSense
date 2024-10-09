from flask_restx import Resource
from flask import Response, jsonify
import threading

from api_satellite import logger
from api_satellite.api.v1 import api
from api_satellite.utils import handle500error

from api_satellite.models.manager import SatelliteManager

model = SatelliteManager()

satellite_ns = api.namespace('satellite', description='Satellite operations')

@satellite_ns.route('/generate_data')
class SatelliteGenerate(Resource):
    """
    Example generation operations
    """
    @api.response(200, 'Example successful')
    @api.response(400, 'Invalid input')
    @api.response(404, 'LLM not found')
    @api.response(500, 'Unknown error')
    def get(self):
        logger.info("GET /satellite/generate_data")
        try:
            logger.info("Starting generation...")
            task_thread = threading.Thread(target=model.start_generation)
            task_thread.start()
            return jsonify({"message": "Generation started"})
        except Exception as e:
            return handle500error(satellite_ns, str(e))

