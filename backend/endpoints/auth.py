from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash
import jwt
from models import User
import bcrypt
import datetime
from cmn_utils import *

auth_blueprint = Blueprint('auth', __name__)

# Login route
@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    try:
        # Query the user using SQLAlchemy
        user = User.query.filter_by(email=email).first()

        # If user is not found or password hash is missing
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 400
        if not user.pass_hash:
            return jsonify({'error': 'Password not set for this user'}), 400

        # Verify the password
        if not bcrypt.checkpw(password.encode('utf-8'), user.pass_hash.encode('utf-8')):
            return jsonify({'error': 'Invalid credentials'}), 400

        # Generate JWT token
        token = jwt.encode(
            {
                'email': user.email, 
                'permission': user.permission,
                'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)  # Token expires in 1 hour
            },
            current_app.config["SECRET_KEY"],
            algorithm='HS256'
        )

        return jsonify({'token': token, 'permission': user.permission}), 200

    except Exception as e:
        # Handle exceptions gracefully (you can customize this)
        print_exception(e)
        return jsonify({'error': 'Server error'}), 500

# Verify Token route (optional)
@auth_blueprint.route('/verify', methods=['GET'])
def verify_token():
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401

    token = auth_header.split(' ')[1]

    try:
        # Decode the token
        decoded = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=['HS256'])
        return jsonify({'decoded': decoded}), 200

    except jwt.ExpiredSignatureError as e :
        print_exception(e)
        return jsonify({'error': 'Token has expired'}), 401

    except jwt.InvalidTokenError as e :
        print_exception(e)
        return jsonify({'error': 'Invalid token'}), 401