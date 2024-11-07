from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from models import User, db
from classes.RC import RC
from classes.UserRepository import UserRepository
from classes.AuthService import AuthService
from classes.ModelValidator import ModelValidator
from classes.DomainClassFactory import DomainClassFactory
import bcrypt
import datetime
from cmn_utils import *


auth_blueprint = Blueprint('auth', __name__)
auth_service: AuthService = AuthService(UserRepository(db), ModelValidator(), DomainClassFactory())  

# Login route
@auth_blueprint.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        response: dict = auth_service.login(email, password)
        if isinstance(response, RC):
           return response.to_json()
    
        return jsonify({
            'access_token': response["access_token"], 
            'refresh_token': response["refresh_token"],
            'permission': response["permission"],
            'company_id': response["company_id"]
        }), E_RC.RC_OK

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE

# Refresh token endpoint
@auth_blueprint.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        current_user = get_jwt_identity()
        
        # Query the user using SQLAlchemy
        response = auth_service.refresh(current_user)
        if isinstance(response, RC):
            return response.to_json()
        
        return jsonify({
            'access_token': response["new_access_token"], 
            'refresh_token': response["new_refresh_token"]
            }), E_RC.RC_OK
    
    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE