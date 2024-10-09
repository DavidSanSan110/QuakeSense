import csv
import os
from api_satellite import logger

class Satellite:
    def __init__(self, id):
        # Obtain path to data folder
        logger.info(f"Creating satellite {id}...")
        self.id = id
        files = os.listdir(os.getcwd() + "/api_satellite/models/data")
        files = sorted([file for file in files if file.endswith(".csv")])
        file = files[id - 1]

        # Load data from CSV file
        with open(os.getcwd() + "/api_satellite/models/data/" + file, newline='') as f:
            reader = csv.reader(f)
            self.data = list(reader)

        # Create a copy of the data
        self.data = self.data[1:]
        #self.datacopy = self.data.copy()
        logger.info(f"Satellite {id} created")

    def generate_vector(self):
        # Get the first x elements of the data
        elements = self.data[:2000] if len(self.data) >= 2000 else self.data
        self.data = self.data[2000:] if len(self.data) >= 2000 else []

        # If the data is empty, reload it
        #if len(self.data) == 0:
        #    self.data = self.datacopy.copy()

        # Return the elements
        elements = [(float(element[1]), float(element[2])) for element in elements]
        return elements