from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from models import UserRepository, User, db
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
        user: User = user_repository.get_user_by_email(email)

        if not user:
            return jsonify({'error': 'Invalid credentials'}), 400
        if not user.pass_hash:
            return jsonify({'error': 'Password not set for this user'}), 400

        # Verify the password
        if not bcrypt.checkpw(password.encode('utf-8'), user.pass_hash.encode('utf-8')):
            return jsonify({'error': 'Invalid credentials'}), 400

        # Generate access and refresh tokens using Flask-JWT-Extended
        additional_claims = {
            'permission': user.permission,  # Include the user's permission in the token
            'company_id': user.company_id  # Include the user's permission in the token
        }
        access_token = create_access_token(identity=user.email, fresh=True, additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=user.email)

        return jsonify({
            'access_token': access_token, 
            'refresh_token': refresh_token,
            'permission': user.permission,
            'company_id': user.company_id
        }), 200

    except Exception as e:
        # Handle exceptions gracefully (you can customize this)
        print_exception(e)
        return jsonify({'error': 'Server error'}), 500

# Verify Token route (using fresh_jwt_required)
@auth_blueprint.route('/verify', methods=['GET'])
@jwt_required(fresh=True) # Require a fresh token for verification
def verify_token():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# Refresh token endpoint
@auth_blueprint.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        current_user = get_jwt_identity()
        
        # Query the user using SQLAlchemy
        user: User = user_repository.get_user_by_email(email=current_user)

        # If user is not found or password hash is missing
        if not user:
            return jsonify({'error': 'Invalid refresh token'}), 400

        additional_claims = {
            'permission': user.permission,  # Include the user's permission in the token
            'company_id': user.company_id  # Include the user's permission in the token
        }
        new_access_token = create_access_token(identity=current_user, fresh=False, additional_claims=additional_claims)
        new_refresh_token = create_refresh_token(identity=current_user) 

        return jsonify({
            'access_token': new_access_token, 
            'refresh_token': new_refresh_token
            }), 200
    
    except Exception as e:
        # Handle exceptions gracefully (you can customize this)
        print_exception(e)
        return jsonify({'error': 'Server error'}), 500