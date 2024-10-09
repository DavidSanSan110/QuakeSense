from api_detector.models.detector import Detector
from api_detector.models.socket import start, emit
import concurrent.futures

class DetectorManager:
    def __init__(self):
        print("Detector Manager initialized")
        start()
        self.detectors = {
            1: Detector(),
            2: Detector(),
            3: Detector(),
            4: Detector(),
            5: Detector(),
            6: Detector()
        }
        print("Detectors loaded")

    def start_detection(self, matrices):
        print(len(matrices))
        results = [None] * len(matrices)

        with concurrent.futures.ThreadPoolExecutor() as executor:

            futures = {executor.submit(self.detectors[i+1].predict, matrix): i for i, matrix in enumerate(matrices)}

            for future in concurrent.futures.as_completed(futures):
                index = futures[future]
                results[index] = future.result()

        print("Detection finished")
        print(results)

        emit("detection", results)


