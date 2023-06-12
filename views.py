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
        parser.add_argument('asset_desc', required=True, help="Asset description cannot be blank!")

        # Parse the incoming request
        args = parser.parse_args()

        # Query the highest asset number in the Asset model and increment it by one
        last_asset = Asset.query.order_by(desc(Asset.asset_number)).first()
        if last_asset is None:
            asset_number = 1
        else:
            asset_number = last_asset.asset_number + 1

        # Concatenate the codes and the new asset number to form the asset name
        asset_name = f"{args['service_code']}-{args['location_code']}-{args['process_code']}-{args['asset_type']}-{asset_number}"

        # Get the asset description from the request data
        asset_desc = args['asset_desc']

        # Return the result as a JSON response
        return {'asset_name': asset_name, 'asset_desc': asset_desc}, 200


api.add_resource(GenerateAsset, '/generate')


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
