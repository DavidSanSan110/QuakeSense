from api_satellite.models.satellite import Satellite
from api_satellite.models.socket import start, emit
import time
from api_satellite import logger

class SatelliteManager:
    def __init__(self):
        logger.info("Creating satellite manager...")
        self.satellites = {
            1: Satellite(1),
            2: Satellite(2),
            3: Satellite(3),
            4: Satellite(4),
            5: Satellite(5),
            6: Satellite(6)
        }
        logger.info("Satellite manager created")

    def start_generation(self):
        start()
        while True:
            matrix = [
                satellite.generate_vector()
                for satellite in self.satellites.values()
            ]
            emit("satellite_data", matrix)
            logger.info("Data emitted")

            # If every vector in the matrix is empty, break the loop
            if all([len(vector) == 0 for vector in matrix]):
                print("All vectors are empty")
                break

            time.sleep(0.1) # Sleep for 0.5 seconds
