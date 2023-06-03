from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:superstar9@localhost/asset_code_names'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
from models import *
class GenerateAsset(Resource):
    def post(self):
        parser = reqparse.RequestParser()

        # Define the data fields to expect in the request
        parser.add_argument('service_code', required=True, help="Service code cannot be blank!")
        parser.add_argument('location_code', required=True, help="Location code cannot be blank!")
        parser.add_argument('process_code', required=True, help="Process code cannot be blank!")
        parser.add_argument('asset_type', required=True, help="Asset type cannot be blank!")

        # Parse the incoming request
        args = parser.parse_args()

        # Concatenate the codes to form the asset name
        asset_name = f"{args['service_code']}-{args['location_code']}-{args['process_code']}-{args['asset_type']}-"

        # Generate the asset description
        asset_desc = f"{args['asset_type']} 1 at {args['location_code']}"

        # Return the result as a JSON response
        return {'asset_name': asset_name, 'asset_desc': asset_desc}, 200

api.add_resource(GenerateAsset, '/generate')

class LocationCode(Resource):
    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('location_code', required=True, help="Location code cannot be blank!")
        parser.add_argument('location_name', required=True, help="Location name cannot be blank!")

        args = parser.parse_args()

        # TODO: Add the new location code to the database

        return {'message': f"Successfully added location {args['location_name']} with code {args['location_code']}."}, 200

api.add_resource(LocationCode, '/location')

class Codes(Resource):
    def get(self):
        # TODO: Fetch all codes from the database

        return {'message': 'Fetched all codes.'}, 200

api.add_resource(Codes, '/codes')

if __name__ == '__main__':
    app.run(debug=True, port=5008)
