from flask import Flask
from flask import request
from flask import jsonify

from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_httpauth import HTTPBasicAuth
from flask_login import current_user, login_user, logout_user
from sqlalchemy import desc
from name_generator import app, db, api, login_manager
from name_generator.models import *
from name_generator.utils import validate_password, send_email, get_duplicate_status
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
from flask import session

auth = HTTPBasicAuth()

class GenerateAsset(Resource):
    def post(self):
        parser = reqparse.RequestParser()

        # Define the data fields to expect in the request
        # parser.add_argument('service_code', required=True, help="Service code cannot be blank!")
        parser.add_argument('location_code', required=True, help="Location code cannot be blank!")
        parser.add_argument('process_code', required=True, help="Process code cannot be blank!")
        parser.add_argument('asset_type', required=True, help="Asset type cannot be blank!")
        parser.add_argument('duplicate_status')
        # parser.add_argument('asset_desc', required=True, help="Asset description cannot be blank!")

        # Parse the incoming request
        args = parser.parse_args()

        # Fetch descriptions based on provided codes
        location_desc = LocationCode.query.filter_by(code=args['location_code']).first().description
        process_desc = ProcessCode.query.filter_by(code=args['process_code']).first().description
        asset_type_desc = AssetType.query.filter_by(code=args['asset_type']).first().description

        # Count the existing assets with the same combination of codes
        local_number = AssetLocation.query.filter(
                                            AssetLocation.location_code.has(code=args['location_code']),
                                            AssetLocation.process_code.has(code=args['process_code']),
                                            AssetLocation.asset_type.has(code=args['asset_type'])
                                        ).count() + 1


        # Query the highest asset number in the Asset model and increment it by one
        last_asset = Asset.query.order_by(desc(Asset.asset_number)).first()
        if last_asset is None:
            asset_number = 1
        else:
            asset_number = last_asset.asset_number + 1

        duplicate_status = args['duplicate_status']
        # Concatenate the codes and the new asset number to form the asset name
        asset_location_name = f"{args['location_code']}-{args['process_code']}-{args['asset_type']}-{local_number:0>4}{duplicate_status}"
        asset_name = f"{args['process_code']}-{args['asset_type']}-{asset_number:0>4}"
   
        # Generate the asset description
        asset_location_desc = f"{process_desc} {asset_type_desc} {local_number} at {location_desc} {'(' if duplicate_status else ''}{get_duplicate_status(duplicate_status)}{')' if duplicate_status else ''}"
        asset_desc = f"{process_desc} {asset_type_desc} asset number: {asset_number}"
     
        # Return the result as a JSON response
        return {'asset_name': asset_name, 'asset_location_name': asset_location_name, 'asset_desc': asset_desc, 'asset_location_desc': asset_location_desc, 'local_number': local_number}, 200


api.add_resource(GenerateAsset, '/generate')


class RegisterAsset(Resource):
    def post(self):
        parser = reqparse.RequestParser()

        # Define the data fields to expect in the request
        # parser.add_argument('service_code', required=True, help="Service code cannot be blank!")
        parser.add_argument('location_code', required=True, help="Location code cannot be blank!")
        parser.add_argument('process_code', required=True, help="Process code cannot be blank!")
        parser.add_argument('asset_type', required=True, help="Asset type cannot be blank!")
        parser.add_argument('asset_description', required=True, help="Asset description cannot be blank!")
        parser.add_argument('asset_location_description', required=True, help="Asset location description cannot be blank!")
        parser.add_argument('local_number', required=True, help="Local number cannot be blank!")
        parser.add_argument('asset_number', required=True, help="Asset number cannot be blank!")
        parser.add_argument('duplicate_status')
        

        # Parse the incoming request
        args = parser.parse_args()

               
        # service_code_obj = ServiceCode.query.filter_by(code=args['service_code']).first()
        location_code_obj = LocationCode.query.filter_by(code=args['location_code']).first()
        process_code_obj = ProcessCode.query.filter_by(code=args['process_code']).first()
        asset_type_obj = AssetType.query.filter_by(code=args['asset_type']).first()

        duplicate_status = args['duplicate_status']

        # Query the highest asset number in the Asset model and increment it by one
        last_asset = Asset.query.order_by(desc(Asset.asset_number)).first()
        if last_asset is None:
            asset_number = 1
        else:
            asset_number = last_asset.asset_number + 1

        # Add the new asset location to the database
        new_asset_location = AssetLocation(location_code=location_code_obj,
                  process_code=process_code_obj, asset_type=asset_type_obj,
                  local_number=args['local_number'],
                  description=args['asset_location_description'], duplicate_status=duplicate_status)
        
        db.session.add(new_asset_location)
        db.session.commit()
        # Add the new asset to the database
        new_asset = Asset(
                  asset_location_id=new_asset_location.id,
                  asset_number=asset_number,
                  description=args['asset_description'])

        db.session.add(new_asset)
        db.session.commit()


        # Return the result as a JSON response
        return {"msg": "Asset registered successfully"}, 200


api.add_resource(RegisterAsset, '/register_asset')


class Codes(Resource):
    def get(self):
        # service_codes = ServiceCode.query.all()
        location_codes = LocationCode.query.all()
        process_codes = ProcessCode.query.all()
        asset_types = AssetType.query.all()

        return {
    # 'service_codes': [{'id': code.id, 'code': code.code, 'description': code.description} for code in service_codes],
    'location_codes': [{'id': code.id, 'code': code.code, 'description': code.description} for code in location_codes],
    'process_codes': [{'id': code.id, 'code': code.code, 'description': code.description} for code in process_codes],
    'asset_types': [{'id': code.id, 'code': code.code, 'description': code.description} for code in asset_types]
}, 200


    def post(self):
        parser = reqparse.RequestParser()  # initialize parser
        parser.add_argument('code_type', required=True)
        parser.add_argument('code', required=True)
        parser.add_argument('description', required=False)
        args = parser.parse_args()  # parse arguments to dictionary

        code_type = args['code_type'][:-6]
        code_value = args['code']
        description = args['description']

        # if code_type.lower() == 'service':
        #     new_code = ServiceCode(code=code_value, description=description)
        if code_type.lower() == 'location':
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

class CodeDetailAPI(Resource):
    def get(self, code_type, id):
        # if code_type.lower() == 'service':
        #     code = ServiceCode.query.get(id)
        if code_type.lower() == 'location':
            code = LocationCode.query.get(id)
        elif code_type.lower() == 'process':
            code = ProcessCode.query.get(id)
        elif code_type.lower() == 'asset':
            code = AssetType.query.get(id)
        else:
            return {"msg": "Invalid code_type in request"}, 400

        if code is None:
            return {"msg": "Code not found"}, 404

        return {'code': code.code, 'description': code.description}, 200
    
    def put(self, code_type, id):
        data = request.get_json()
        
        # if code_type.lower() == 'service_codes':
        #     code = ServiceCode.query.get(id)
        if code_type.lower() == 'location_codes':
            code = LocationCode.query.get(id)
        elif code_type.lower() == 'process_codes':
            code = ProcessCode.query.get(id)
        elif code_type.lower() == 'asset_types':
            code = AssetType.query.get(id)
        else:
            return {"msg": "Invalid code_type in request"}, 400

        if code is None:
            return {"msg": "Code not found"}, 404

        code.code = data['code']
        code.description = data['description']
        db.session.commit()

        return {"msg": "Code updated successfully"}, 200

    def delete(self, code_type, id):
        # if code_type.lower() == 'service_codes':
        #     code = ServiceCode.query.get(id)
        if code_type.lower() == 'location_codes':
            code = LocationCode.query.get(id)
        elif code_type.lower() == 'process_codes':
            code = ProcessCode.query.get(id)
        elif code_type.lower() == 'asset_types':
            code = AssetType.query.get(id)
        else:
            return {"msg": "Invalid code_type in request"}, 400

        if code is None:
            return {"msg": "Code not found"}, 404

        db.session.delete(code)
        db.session.commit()

        return {"msg": "Code deleted successfully"}, 200

api.add_resource(CodeDetailAPI, '/codes/<string:code_type>/<int:id>')

######################################### USERS ############################################

# # User Resource
# class UserAPI(Resource):
#     def get(self, user_id):
#         user = User.query.get(user_id)
#         if user:
#             return {
#                 'id': user.id,
#                 'email': user.email,
#                 'is_admin': user.is_admin,
#                 'is_first_login': user.is_first_login
#             }, 200
#         else:
#             return {"error": "User not found"}, 404

#     def put(self, user_id):
#         parser = reqparse.RequestParser()  # initialize parser
#         parser.add_argument('email', required=False)
#         parser.add_argument('is_admin', required=False, type=bool)
#         parser.add_argument('is_first_login', required=False, type=bool)
#         args = parser.parse_args()  # parse arguments to dictionary

#         user = User.query.get(user_id)
#         if user:
#             if args['email']:
#                 user.email = args['email']
#             if args['is_admin'] is not None:
#                 user.is_admin = args['is_admin']
#             if args['is_first_login'] is not None:
#                 user.is_first_login = args['is_first_login']

#             db.session.commit()

#             return {"msg": "User updated successfully"}, 200
#         else:
#             return {"error": "User not found"}, 404

#     def delete(self, user_id):
#         user = User.query.get(user_id)
#         if user:
#             db.session.delete(user)
#             db.session.commit()

#             return {"msg": "User deleted successfully"}, 200
#         else:
#             return {"error": "User not found"}, 404

# # User List Resource
# class UserListAPI(Resource):
#     def get(self):
#         users = User.query.all()
#         return [{
#             'id': user.id,
#             'email': user.email,
#             'is_admin': user.is_admin,
#             'is_first_login': user.is_first_login
#         } for user in users], 200

#     def post(self):
#         parser = reqparse.RequestParser()  # initialize parser
#         parser.add_argument('email', required=True)
#         parser.add_argument('is_admin', required=True)
#         args = parser.parse_args()  # parse arguments to dictionary

#         email = args['email']
#         is_admin = args['is_admin'].lower() == 'true'
#         first_part = email[0]
#         last_name = email.split('@')[0].split('.')[1][:3]
#         digits = ''.join(random.choice(string.digits) for i in range(2))
#         password = (first_part + last_name + digits).capitalize()
#         hashed_password = generate_password_hash(password)

#         new_user = User(email=email, password_hash=hashed_password, is_first_login=True, is_admin=is_admin)

#         db.session.add(new_user)
#         db.session.commit()
#         send_email(email, password)

#         return {"msg": "User added successfully", "password": password}, 201

# api.add_resource(UserAPI, '/users/<int:user_id>')
# api.add_resource(UserListAPI, '/users')


# @app.route('/register', methods=['POST'])
# def register():
#     data = request.get_json()
#     email = data.get('email')
#     password = data.get('password')

#     # Check if user already exists
#     if User.find_by_email(email):
#         return jsonify({'message': f'User {email} already exists'}), 400

#     # Validate the password
#     password_validation_message = validate_password(password)
#     if password_validation_message != "Strong password":
#         return jsonify({'message': password_validation_message}), 400

#     # If validation passed, create the user
#     user = User(email=email)
#     user.set_password(password)

#     db.session.add(user)
#     db.session.commit()
    
#     return jsonify({'message': 'User registered successfully'}), 201

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
        # session['user'] = user.to_dict()
        session.modified = True
        # print(session['user'])
        return jsonify({'message': 'Logged in successfully'})
    else:
        return jsonify({'message': 'Invalid email or password'}), 401
    
@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    # Check if the current_user is authenticated
    # print(current_user.id)
    # current_user = session['user']
    if current_user:
        # If a user is logged in, return their data
        return jsonify(current_user.to_dict())
    else:
        # If no user is logged in, return an appropriate error status
        return jsonify({'error': 'Not logged in'}), 401


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

############################# ASSETS ###################################

class AssetListResource(Resource):
    def get(self):
        assets = AssetLocation.query.all()
        return [{'id': asset.id, 'name': asset.name(), 'description': asset.description} for asset in assets]


class AssetDetailResource(Resource):
    def get(self, asset_id):
        asset = AssetLocation.query.get_or_404(asset_id)
        return {'id': asset.id, 'name': asset.name(), 'description': asset.description}

    def put(self, asset_id):
        asset = AssetLocation.query.get_or_404(asset_id)
        data = request.get_json()
        asset.description = data.get('description', asset.description)
        db.session.commit()
        return {'id': asset.id, 'name': asset.name(), 'description': asset.description}


class MatchingAssetsResource(Resource):
    def get(self):
        codes = request.args
        matching_assets = AssetLocation.query.filter_by(location_code_id=codes.get('location_code_id'),
                                                process_code_id=codes.get('process_code_id'),
                                                asset_type_id=codes.get('asset_type_id')).all()
        ans = [{'id': asset.id, 'name': asset.name(), 'description': asset.description} for asset in matching_assets]
        # print(ans)
        return ans


api.add_resource(AssetListResource, '/api/assets')
api.add_resource(AssetDetailResource, '/api/assets/<int:asset_id>')
api.add_resource(MatchingAssetsResource, '/api/assets/matching')

if __name__ == '__main__':
    app.run(debug=True, port=5009)
