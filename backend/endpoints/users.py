from flask import Blueprint, request, jsonify, current_app
from models import db  
from classes.repositories.UserRepository import UserRepository
from classes.repositories.CompanyRepository import CompanyRepository
from classes.validators.ModelValidator import ModelValidator
from classes.factories.DomainClassFactory import DomainClassFactory
from classes.dataclass.User import User
from classes.services.UserService import UserService
from classes.utilities.RC import RC, E_RC
from cmn_utils import *
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt


users_blueprint = Blueprint('users', __name__)
user_service = UserService(UserRepository(db), CompanyRepository(db), ModelValidator(), DomainClassFactory())

# Create user route
@users_blueprint.route('/create-user', methods=['POST'])
@jwt_required() 
def create_user():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        
        
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
        mobile_phone = data.get('mobile_phone')
        
        # Create new user object
        rc: RC = user_service.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            company_name=company_name, 
            role=role,
            permission=permission,
            password=password,
            salary=salary,
            work_capacity=work_capacity,
            employment_start_str=employment_start_str,
            employment_end_str=employment_end_str,
            weekend_choice=weekend_choice,
            mobile_phone=mobile_phone,
            user_permission=user_permission,
        )

        return rc.to_json()
    
    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE

# Update user route
@users_blueprint.route('/update-user', methods=['PUT'])
@jwt_required() 
def update_user():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        
        data: dict = request.get_json()
        user_email = data.get('email')  
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        mobile_phone = data.get('mobile_phone')
        role = data.get('role')
        permission = data.get('permission')
        salary = data.get('salary')
        work_capacity = data.get('work_capacity')
        password = data.get('password')
        employment_start_str = data.get('employment_start')
        employment_end_str = data.get('employment_end')
        weekend_choice = data.get('weekend_choice')

        rc: RC = user_service.update_user(user_email, user_permission, first_name=first_name, last_name=last_name, mobile_phone=mobile_phone, \
            role=role, permission=permission, salary=salary, work_capacity=work_capacity,\
                employment_start_str=employment_start_str, employment_end_str=employment_end_str, weekend_choice=weekend_choice,\
                    password=password)
        
        return rc.to_json()

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE

# Remove user 
@users_blueprint.route('/remove-user/<string:user_email>', methods=['PUT']) 
@jwt_required() 
def remove_user(user_email):
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
         
    
        data: dict = request.get_json()
        employment_end_str = data.get('employment_end')  # Get employment_end from request

        rc: RC = user_service.delete_user(user_permission, user_email, employment_end_str)

        return rc.to_json()
        
    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE

# Get active users route
@users_blueprint.route('/active', methods=['GET'])
@jwt_required() 
def get_active_users():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        user_data: dict = user_service.get_active_users(user_permission, user_company_id)
        if isinstance(user_data, RC):
            return user_data.to_json()
            
        return jsonify(user_data), E_RC.RC_OK

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Internal server error'}), E_RC.RC_ERROR_DATABASE
    
@users_blueprint.route('/not-active', methods=['GET'])
@jwt_required() 
def get_inactive_users():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        user_data: dict = user_service.get_inactive_users(user_permission, user_company_id)
        if isinstance(user_data, RC):
            return user_data.to_json()
            
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

        user_data: dict = user_service.get_all_users(user_permission, user_company_id)
        if isinstance(user_data, RC):
            return user_data.to_json()
            
        return jsonify(user_data), E_RC.RC_OK

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Internal server error'}), E_RC.RC_ERROR_DATABASE

@users_blueprint.route('/user-by-email/<string:email>', methods=['GET'])
@jwt_required() 
def user_by_email(email):
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        
        requested_user: User = user_service.get_user_by_email(user_permission, current_user_email, user_company_id, email)
        if isinstance (requested_user,RC):
            return requested_user.to_json()
        
        return jsonify(requested_user), E_RC.RC_OK

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

        rc: RC = user_service.change_password(user_permission, current_user_email, user_company_id, current_user_email, new_password)
        
        return rc.to_json()

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Failed to change password'}), E_RC.RC_ERROR_DATABASE
    
@users_blueprint.route('/reactivate-user', methods=['PUT'])
@jwt_required()
def reactivate_user():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        data = request.get_json()
        user_email = data.get('user_email')

        rc: RC = user_service.reactivate_user(user_permission, user_email)
        
        return rc.to_json()

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Failed to change password'}), E_RC.RC_ERROR_DATABASE
    
