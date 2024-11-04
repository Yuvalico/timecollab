from flask import Blueprint, request, jsonify, current_app
from models import UserRepository, User, Company, CompanyRepository, db  
import bcrypt
from cmn_utils import *
from cmn_defs import *
from datetime import datetime, timezone
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt


users_blueprint = Blueprint('users', __name__)
user_repository = UserRepository(db)
company_repository = CompanyRepository(db)

# Create user route
@users_blueprint.route('/create-user', methods=['POST'])
@jwt_required() 
def create_user():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        if E_PERMISSIONS.to_enum(user_permission) > E_PERMISSIONS.net_admin:
            return jsonify({'error': 'Unauthorized access'}), 403 
        
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
                return jsonify({'error': 'Missing mandatory user field'}), 400

        permission_int = E_PERMISSIONS.to_enum(permission)
        if permission_int is None:
            return jsonify({'error': 'Invalid permission type'}), 403

        # Check if user already exists using SQLAlchemy
        existing_user: User = user_repository.get_user_by_email(email) 
        if existing_user:
            return jsonify({'error': 'User email already exists'}), 400

        # Get the company_id using SQLAlchemy
        company: Company = company_repository.get_company_by_name(company_name)
        if not company:
            return jsonify({'error': 'Company not found'}), 404

        # Create new user object
        new_user = user_repository.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            company_id=company.company_id,  # Associate with the company
            role=role,
            permission=permission_int,
            password=password,
            salary=salary,
            work_capacity=work_capacity,
            employment_start=employment_start_str,
            employment_end=employment_end_str,
            weekend_choice=weekend_choice
        )
        if new_user:
            return jsonify({'message': 'User registered successfully', 'user': new_user.to_dict()}), 201 

        else:
            return jsonify({'message': 'Failed to create new user'}), 500 

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Server error'}), 500

# Update user route
@users_blueprint.route('/update-user', methods=['PUT'])
@jwt_required() 
def update_user():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        if E_PERMISSIONS.to_enum(user_permission) > E_PERMISSIONS.net_admin:
            return jsonify({'error': 'Unauthorized access'}), 403 
        
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
        if not user:
            return jsonify({'error': 'User not found'}), 404

        success: bool = user_repository.update_user(user, first_name, last_name=last_name, mobile_phone=mobile_phone, \
            role=role, permission=permission, salary=salary, work_capacity=work_capacity,\
                employment_start_str=employment_start_str, employment_end_str=employment_end_str, weekend_choice=weekend_choice,\
                    password=password)
        
        if success:
            return jsonify({'message': 'User updated successfully', 'user': user.to_dict()}), 200
        else:
            return jsonify({'message': 'User update Failed'}), 500

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Server error'}), 500

# Remove user 
@users_blueprint.route('/remove-user/<string:user_email>', methods=['PUT']) 
@jwt_required() 
def remove_user(user_email):
    try:
        current_user_email, user_permission, user_company_email = extract_jwt()
        if E_PERMISSIONS.to_enum(user_permission) > E_PERMISSIONS.net_admin:
            return jsonify({'error': 'Unauthorized access'}), 403 
    
        data = request.get_json()
        employment_end_str = data.get('employment_end')  # Get employment_end from request


        # Soft delete user using SQLAlchemy
        user = user_repository.get_user_by_email(user_email)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        success: bool = user_repository.delete_user(user, employment_end_str)

        if success:
            return jsonify({'message': 'User removed successfully', 'user': user.to_dict()}), 200
        else:
            return jsonify({'message': 'User remove failed'}), 500
        
    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Server error'}), 500

# Get active users route
@users_blueprint.route('/active', methods=['GET'])
@jwt_required() 
def get_active_users():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        if E_PERMISSIONS.to_enum(user_permission) > E_PERMISSIONS.employer:
            return jsonify({'error': 'Unauthorized access'}), 403 
        
        if E_PERMISSIONS.to_enum(user_permission) ==E_PERMISSIONS.net_admin:
            active_users: list[User] = user_repository.get_all_active_users()
        
        if E_PERMISSIONS.to_enum(user_permission) == E_PERMISSIONS.employer:
            active_users: list[User] = user_repository.get_all_active_users(user_company_id)

        user_data = []
        for user in active_users:  # No need to unpack company here
            user_dict = user.to_dict()
            user_dict['company_name'] = company_repository.get_company_by_id(user.company_id).company_name  # You might need to fetch the company name separately
            user_data.append(user_dict)

        return jsonify(user_data), 200

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Internal server error'}), 500

# Get all users route
@users_blueprint.route('/', methods=['GET'])
@jwt_required() 
def get_all_users():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        if E_PERMISSIONS.to_enum(user_permission) > E_PERMISSIONS.employer:
            return jsonify({'error': 'Unauthorized access'}), 403 
        
        if E_PERMISSIONS.to_enum(user_permission) ==E_PERMISSIONS.net_admin:
            active_users: list[User] = user_repository.get_active_users()
        
        if E_PERMISSIONS.to_enum(user_permission) == E_PERMISSIONS.employer:
            active_users: list[User] = user_repository.get_active_users(user_company_id)

        user_data = []
        for user in active_users:  # No need to unpack company here
            user_dict = user.to_dict()
            user_dict['company_name'] = user.company.company_name  # You might need to fetch the company name separately
            user_data.append(user_dict)

        return jsonify(user_data), 200

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Internal server error'}), 500

@users_blueprint.route('/user-by-email/<string:email>', methods=['GET'])
@jwt_required() 
def user_by_email(email):
    try:
        # Get the identity (email) of the current user from the JWT
        current_user_email, user_permission, user_company_id = extract_jwt()
        # Query the requested user by email
        requested_user: User = user_repository.get_user_by_email(email=email)
        if not requested_user:
            return jsonify({'error': 'User not found'}), 404

        if current_user_email == email:
            return jsonify(requested_user.to_dict()), 200
        
        # Check if the current user is the requested user or an employer of the same company
        if user_permission == E_PERMISSIONS.net_admin or (requested_user.company_id and 
                                           user_company_id == requested_user.company_id and
                                           user_permission == E_PERMISSIONS.employer): 
            return jsonify(requested_user.to_dict()), 200
        else:
            return jsonify({'error': 'Unauthorized access'}), 403

    except Exception as e:
        print_exception(e)
        return jsonify({'error': str(e)}), 500
    
@users_blueprint.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        data = request.get_json()
        new_password = data.get('new_password')

        user = user_repository.get_user_by_email(current_user_email)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Hash the new password
        success: bool = user_repository.change_password(new_password)
        if success:
            return jsonify({'message': 'Password changed successfully'}), 200
        else:
            return jsonify({'message': 'Password change failed'}), 500

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Failed to change password'}), 500
    
