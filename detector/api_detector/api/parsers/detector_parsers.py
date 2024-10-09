from flask_restx import reqparse

matrices_parser = reqparse.RequestParser()
matrices_parser.add_argument('matrices', type=list, required=True, help='The matrices to use for generation', location='json')