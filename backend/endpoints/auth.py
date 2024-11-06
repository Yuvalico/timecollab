from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from models import User, db
from classes.RC import RC
from classes.UserRepository import UserRepository
import bcrypt
import datetime
from cmn_utils import *


auth_blueprint = Blueprint('auth', __name__)
user_repository = UserRepository(db)  

# Login route
@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    remember = data.get('remember')
    try:
        user: User|RC = user_repository.get_user_by_email(email)
        if isinstance (user, RC):
            return createRcjson(user)
        
        if not user.pass_hash:
            return jsonify({'error': 'Password not set for this user'}), E_RC.RC_INVALID_INPUT

        if not bcrypt.checkpw(password.encode('utf-8'), user.pass_hash.encode('utf-8')):
            return jsonify({'error': 'Invalid credentials'}), E_RC.RC_INVALID_INPUT

        additional_claims = {
            'permission': user.permission,  
            'company_id': user.company_id  
        }
        access_token = create_access_token(identity=user.email, fresh=True, additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=user.email)

        return jsonify({
            'access_token': access_token, 
            'refresh_token': refresh_token,
            'permission': user.permission,
            'company_id': user.company_id
        }), E_RC.RC_OK

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE

# Verify Token route 
@auth_blueprint.route('/verify', methods=['GET'])
@jwt_required(fresh=True) 
def verify_token():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), E_RC.RC_OK

# Refresh token endpoint
@auth_blueprint.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        current_user = get_jwt_identity()
        
        # Query the user using SQLAlchemy
        user: User|RC = user_repository.get_user_by_email(email=current_user)
        if isinstance (user, RC):
            return createRcjson(user)

        additional_claims = {
            'permission': user.permission,  
            'company_id': user.company_id 
        }
        new_access_token = create_access_token(identity=current_user, fresh=False, additional_claims=additional_claims)
        new_refresh_token = create_refresh_token(identity=current_user) 

        return jsonify({
            'access_token': new_access_token, 
            'refresh_token': new_refresh_token
            }), E_RC.RC_OK
    
    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE