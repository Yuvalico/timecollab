from flask import Blueprint, request, jsonify, current_app
from models import Company, db  
from classes import UserRepository, CompanyRepository
from classes.User import User
from classes.Company import Company
from classes.RC import RC
import bcrypt
from cmn_utils import *
from cmn_defs import *
from datetime import datetime, timezone
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt


users_blueprint = Blueprint('users', __name__)
user_repository = UserRepository.UserRepository(db)
company_repository = CompanyRepository.CompanyRepository(db)

# Create user route
@users_blueprint.route('/create-user', methods=['POST'])
@jwt_required() 
def create_user():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        if E_PERMISSIONS.to_enum(user_permission) > E_PERMISSIONS.net_admin:
            return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED 
        
        data = request.get_json()
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        password = data.get('password')
        company_name = data.get('company_name')
        role = data.get('role')
        permission = data.get('permission')
        salary = data.get('salary')
        work_capacity = data.get('work_capacity')
        employment_start_str = data.get('employment_start')
        employment_end_str = data.get('employment_end')
        weekend_choice = data.get('weekend_choice')
        
        if not first_name or not last_name or not email or not password or not company_name or not company_name\
            or not role or not permission or not salary or not work_capacity or not employment_start_str:
                return jsonify({'error': 'Missing mandatory user field'}), E_RC.RC_INVALID_INPUT

        permission_int = E_PERMISSIONS.to_enum(permission)
        if permission_int is None:
            return jsonify({'error': 'Invalid permission type'}), E_RC.RC_UNAUTHORIZED

        # Check if user already exists using SQLAlchemy
        existing_user: User|RC = user_repository.get_user_by_email(email) 
        if not isinstance (existing_user,RC):
            return jsonify({'error': 'User email already exists'}), E_RC.RC_INVALID_INPUT
        
        # Get the company_id using SQLAlchemy
        company: Company = company_repository.get_company_by_name(company_name)
        if isinstance(company, RC):
            return createRcjson(company)

        # Create new user object
        rc: RC = user_repository.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            company_id=company.company_id,  # Associate with the company
            role=role,
            permission=permission_int,
            password=password,
            salary=salary,
            work_capacity=work_capacity,
            employment_start_str=employment_start_str,
            employment_end_str=employment_end_str,
            weekend_choice=weekend_choice
        )

        return createRcjson(rc)
    
    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE

# Update user route
@users_blueprint.route('/update-user', methods=['PUT'])
@jwt_required() 
def update_user():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        if E_PERMISSIONS.to_enum(user_permission) > E_PERMISSIONS.net_admin:
            return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED 
        
        data: dict = request.get_json()
        user_email = data.get('email')  # Get user_email from the request body
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        mobile_phone = data.get('mobile_phone')
        email = data.get('email')
        role = data.get('role')
        permission = data.get('permission')
        salary = data.get('salary')
        work_capacity = data.get('work_capacity')
        password = data.get('password')
        employment_start_str = data.get('employment_start')
        employment_end_str = data.get('employment_end')
        weekend_choice = data.get('weekend_choice')

        # Get the user using SQLAlchemy
        user: User = user_repository.get_user_by_email(user_email)
        if isinstance (user,RC):
            return createRcjson(user)

        rc: RC = user_repository.update_user(user, first_name, last_name=last_name, mobile_phone=mobile_phone, \
            role=role, permission=permission, salary=salary, work_capacity=work_capacity,\
                employment_start_str=employment_start_str, employment_end_str=employment_end_str, weekend_choice=weekend_choice,\
                    password=password)
        
        return createRcjson(rc)

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE

# Remove user 
@users_blueprint.route('/remove-user/<string:user_email>', methods=['PUT']) 
@jwt_required() 
def remove_user(user_email):
    try:
        current_user_email, user_permission, user_company_email = extract_jwt()
        if E_PERMISSIONS.to_enum(user_permission) > E_PERMISSIONS.net_admin:
            return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED 
    
        data = request.get_json()
        employment_end_str = data.get('employment_end')  # Get employment_end from request


        # Soft delete user using SQLAlchemy
        user = user_repository.get_user_by_email(user_email)
        if isinstance (user,RC):
            return createRcjson(user)

        rc: RC = user_repository.delete_user(user, employment_end_str)

        createRcjson(rc)
        
    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE

# Get active users route
@users_blueprint.route('/active', methods=['GET'])
@jwt_required() 
def get_active_users():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        if E_PERMISSIONS.to_enum(user_permission) > E_PERMISSIONS.employer:
            return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED 
        
        if E_PERMISSIONS.to_enum(user_permission) ==E_PERMISSIONS.net_admin:
            active_users: list[User] = user_repository.get_all_active_users()
        
        if E_PERMISSIONS.to_enum(user_permission) == E_PERMISSIONS.employer:
            active_users: list[User] = user_repository.get_all_active_users(user_company_id)

        user_data = []
        for user in active_users:  # No need to unpack company here
            user_dict = user.to_dict()
            user_dict['company_name'] = company_repository.get_company_by_id(user.company_id).company_name  # You might need to fetch the company name separately
            user_data.append(user_dict)

        return jsonify(user_data), E_RC.RC_OK

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Internal server error'}), E_RC.RC_ERROR_DATABASE

# Get all users route
@users_blueprint.route('/', methods=['GET'])
@jwt_required() 
def get_all_users():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        if E_PERMISSIONS.to_enum(user_permission) > E_PERMISSIONS.employer:
            return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED 
        
        if E_PERMISSIONS.to_enum(user_permission) ==E_PERMISSIONS.net_admin:
            active_users: list[User] = user_repository.get_active_users()
        
        if E_PERMISSIONS.to_enum(user_permission) == E_PERMISSIONS.employer:
            active_users: list[User] = user_repository.get_active_users(user_company_id)

        user_data = []
        for user in active_users:  # No need to unpack company here
            user_dict = user.to_dict()
            user_dict['company_name'] = user.company.company_name  # You might need to fetch the company name separately
            user_data.append(user_dict)

        return jsonify(user_data), E_RC.RC_OK

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Internal server error'}), E_RC.RC_ERROR_DATABASE

@users_blueprint.route('/user-by-email/<string:email>', methods=['GET'])
@jwt_required() 
def user_by_email(email):
    try:
        # Get the identity (email) of the current user from the JWT
        current_user_email, user_permission, user_company_id = extract_jwt()
        # Query the requested user by email
        requested_user: User = user_repository.get_user_by_email(email=email)
        if isinstance (requested_user,RC):
            return createRcjson(requested_user)
        
        if current_user_email == email:
            return jsonify(requested_user.to_dict()), E_RC.RC_OK
        
        # Check if the current user is the requested user or an employer of the same company
        if user_permission == E_PERMISSIONS.net_admin or (requested_user.company_id and 
                                           user_company_id == requested_user.company_id and
                                           user_permission == E_PERMISSIONS.employer): 
            return jsonify(requested_user.to_dict()), E_RC.RC_OK
        else:
            return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED

    except Exception as e:
        print_exception(e)
        return jsonify({'error': str(e)}), E_RC.RC_ERROR_DATABASE
    
@users_blueprint.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        data = request.get_json()
        new_password = data.get('new_password')

        user = user_repository.get_user_by_email(current_user_email)
        if isinstance (user,RC):
            return createRcjson(user)

        # Hash the new password
        rc: RC = user_repository.change_password(new_password)
        
        return createRcjson(rc)

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Failed to change password'}), E_RC.RC_ERROR_DATABASE
    
