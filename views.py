from flask import Flask
from flask import request
from flask import jsonify

from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_httpauth import HTTPBasicAuth
from flask_login import current_user, login_user, logout_user
from sqlalchemy import desc
from name_generator import app, db, api
from name_generator.models import *
from name_generator.utils import validate_password


auth = HTTPBasicAuth()

class GenerateAsset(Resource):
    def post(self):
        parser = reqparse.RequestParser()

        # Define the data fields to expect in the request
        parser.add_argument('service_code', required=True, help="Service code cannot be blank!")
        parser.add_argument('location_code', required=True, help="Location code cannot be blank!")
        parser.add_argument('process_code', required=True, help="Process code cannot be blank!")
        parser.add_argument('asset_type', required=True, help="Asset type cannot be blank!")
        # parser.add_argument('asset_desc', required=True, help="Asset description cannot be blank!")

        # Parse the incoming request
        args = parser.parse_args()

        # Fetch descriptions based on provided codes
        location_desc = LocationCode.query.filter_by(code=args['location_code']).first().description
        process_desc = ProcessCode.query.filter_by(code=args['process_code']).first().description
        asset_type_desc = AssetType.query.filter_by(code=args['asset_type']).first().description

        # Count the existing assets with the same combination of codes
        local_number = Asset.query.filter(
                                            Asset.service_code.has(code=args['service_code']),
                                            Asset.location_code.has(code=args['location_code']),
                                            Asset.process_code.has(code=args['process_code']),
                                            Asset.asset_type.has(code=args['asset_type'])
                                        ).count() + 1


        # Query the highest asset number in the Asset model and increment it by one
        last_asset = Asset.query.order_by(desc(Asset.asset_number)).first()
        if last_asset is None:
            asset_number = 1
        else:
            asset_number = last_asset.asset_number + 1

        # Concatenate the codes and the new asset number to form the asset name
        asset_name = f"{args['service_code']}-{args['location_code']}-{args['process_code']}-{args['asset_type']}-{asset_number}"
   
        # Generate the asset description
        asset_desc = f"{process_desc} {asset_type_desc} {local_number} at {location_desc}"
     
        # Return the result as a JSON response
        return {'asset_name': asset_name, 'asset_desc': asset_desc, 'local_number': local_number}, 200


api.add_resource(GenerateAsset, '/generate')


class RegisterAsset(Resource):
    def post(self):
        parser = reqparse.RequestParser()

        # Define the data fields to expect in the request
        parser.add_argument('service_code', required=True, help="Service code cannot be blank!")
        parser.add_argument('location_code', required=True, help="Location code cannot be blank!")
        parser.add_argument('process_code', required=True, help="Process code cannot be blank!")
        parser.add_argument('asset_type', required=True, help="Asset type cannot be blank!")
        parser.add_argument('description', required=True, help="Description cannot be blank!")
        parser.add_argument('local_number', required=True, help="Description cannot be blank!")
        

        # Parse the incoming request
        args = parser.parse_args()

               
        service_code_obj = ServiceCode.query.filter_by(code=args['service_code']).first()
        location_code_obj = LocationCode.query.filter_by(code=args['location_code']).first()
        process_code_obj = ProcessCode.query.filter_by(code=args['process_code']).first()
        asset_type_obj = AssetType.query.filter_by(code=args['asset_type']).first()

        # Query the highest asset number in the Asset model and increment it by one
        last_asset = Asset.query.order_by(desc(Asset.asset_number)).first()
        if last_asset is None:
            asset_number = 1
        else:
            asset_number = last_asset.asset_number + 1

        # Add the new asset to the database
        new_asset = Asset(service_code=service_code_obj, location_code=location_code_obj,
                  process_code=process_code_obj, asset_type=asset_type_obj, 
                  asset_number=asset_number, local_number=args['local_number'], 
                  description=args['description'])

        db.session.add(new_asset)
        db.session.commit()


        # Return the result as a JSON response
        return {"msg": "Asset registered successfully"}, 200


api.add_resource(RegisterAsset, '/register_asset')


class Codes(Resource):
    def get(self):
        service_codes = ServiceCode.query.all()
        location_codes = LocationCode.query.all()
        process_codes = ProcessCode.query.all()
        asset_types = AssetType.query.all()

        return {
    'service_codes': [{'code': code.code, 'description': code.description} for code in service_codes],
    'location_codes': [{'code': code.code, 'description': code.description} for code in location_codes],
    'process_codes': [{'code': code.code, 'description': code.description} for code in process_codes],
    'asset_types': [{'code': code.code, 'description': code.description} for code in asset_types]
}, 200


    def post(self):
        parser = reqparse.RequestParser()  # initialize parser
        parser.add_argument('code_type', required=True)
        parser.add_argument('code', required=True)
        parser.add_argument('description', required=False)
        args = parser.parse_args()  # parse arguments to dictionary

        code_type = args['code_type']
        code_value = args['code']
        description = args['description']

        if code_type.lower() == 'service':
            new_code = ServiceCode(code=code_value, description=description)
        elif code_type.lower() == 'location':
            new_code = LocationCode(code=code_value, description=description)
        elif code_type.lower() == 'process':
            new_code = ProcessCode(code=code_value, description=description)
        elif code_type.lower() == 'asset':
            new_code = AssetType(code=code_value, description=description)
        else:
            return {"msg": "Invalid code_type in request"}, 400

        db.session.add(new_code)
        db.session.commit()

        return {"msg": "Code added successfully"}, 201

api.add_resource(Codes, '/codes')

######################################### USERS ############################################

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Check if user already exists
    if User.find_by_email(email):
        return jsonify({'message': f'User {email} already exists'}), 400

    # Validate the password
    password_validation_message = validate_password(password)
    if password_validation_message != "Strong password":
        return jsonify({'message': password_validation_message}), 400

    # If validation passed, create the user
    user = User(email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

@auth.verify_password
def verify_password(email, password):
    user = User.query.filter_by(email=email).first()
    if user and user.verify_password(password):
        return user
    
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and user.verify_password(data['password']):
        login_user(user)
        return jsonify({'message': 'Logged in successfully'})
    else:
        return jsonify({'message': 'Invalid email or password'}), 401

@app.route('/logout')
@auth.login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/change_password', methods=['POST'])
@auth.login_required
def change_password():
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if old_password is None or new_password is None:
        return jsonify({'message': 'Missing old or new password'}), 400
    
    if not current_user.verify_password(old_password):
        return jsonify({'message': 'Invalid current password'}), 400

    current_user.set_password(new_password)
    db.session.commit()

    return jsonify({'message': 'Password changed successfully'})

if __name__ == '__main__':
    app.run(debug=True, port=5009)
