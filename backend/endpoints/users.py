from flask import Blueprint, request, jsonify, current_app
from models import User, Company, db  
import bcrypt
from cmn_utils import *
from cmn_defs import *
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt


users_blueprint = Blueprint('users', __name__)

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

        permission_int = E_PERMISSIONS.to_enum(permission)
        if permission_int is None:
            return jsonify({'error': 'Invalid permission type'}), 400

        # Check if user already exists using SQLAlchemy
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'User already exists'}), 400

        # Get the company_id using SQLAlchemy
        company = Company.query.filter_by(company_name=company_name).first()
        if not company:
            return jsonify({'error': 'Company not found'}), 404

        # Create new user object
        new_user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            company_id=company.company_id,  # Associate with the company
            role=role,
            permission=permission_int,
            pass_hash=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            is_active=True,
            salary=salary,
            work_capacity=work_capacity
        )

        # Add and commit using SQLAlchemy
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'User registered successfully', 'user': new_user.to_dict()}), 201 

    except Exception as e:
        db.session.rollback()  # Rollback in case of an error
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
        
        data = request.get_json()
        user_id = data.get('id')  # Get user_id from the request body
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        mobile_phone = data.get('mobile_phone')
        email = data.get('email')
        role = data.get('role')
        permission = data.get('permission')
        salary = data.get('salary')
        work_capacity = data.get('work_capacity')

        # Get the user using SQLAlchemy
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Update user attributes
        user.first_name = first_name
        user.last_name = last_name
        user.mobile_phone = mobile_phone
        user.email = email
        user.role = role
        user.permission = permission
        user.salary = salary
        user.work_capacity = work_capacity

        # Commit changes using SQLAlchemy
        db.session.commit()

        return jsonify({'message': 'User updated successfully', 'user': user.to_dict()}), 200

    except Exception as e:
        db.session.rollback()
        print_exception(e)
        return jsonify({'error': 'Server error'}), 500

# Remove user route (soft delete)
@users_blueprint.route('/remove-user/<string:user_id>', methods=['PUT']) 
@jwt_required() 
def remove_user(user_id):
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        if E_PERMISSIONS.to_enum(user_permission) > E_PERMISSIONS.net_admin:
            return jsonify({'error': 'Unauthorized access'}), 403 
    
        # data = request.get_json()
        # user_id = data.get('id')  # Get user_id from the request body

        # Soft delete user using SQLAlchemy
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user.is_active = False
        db.session.commit()

        return jsonify({'message': 'User removed successfully', 'user': user.to_dict()}), 200

    except Exception as e:
        db.session.rollback()
        print_exception(e)
        return jsonify({'error': 'Server error'}), 500

# Get active users route
@users_blueprint.route('/active', methods=['GET'])
@jwt_required() 
def get_active_users():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        if E_PERMISSIONS.to_enum(user_permission) > E_PERMISSIONS.net_admin:
            return jsonify({'error': 'Unauthorized access'}), 403 
        
        # Query active users using SQLAlchemy and join with companies
        active_users: list[User] = (
            db.session.query(User, Company)
            .join(Company, User.company_id == Company.company_id)
            .filter(User.is_active == True)
            .all()
        )

        # Format the results
        user_data = []
        for user, company in active_users:
            user_dict = user.to_dict()  # Assuming you have a to_dict() method
            user_dict['company_name'] = company.company_name
            user_dict['permission'] = user.permission
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

        if E_PERMISSIONS.to_enum(user_permission) > E_PERMISSIONS.net_admin:
            return jsonify({'error': 'Unauthorized access'}), 403 
        
        # Query all users using SQLAlchemy and join with companies
        all_users = (
            db.session.query(User, Company)
            .join(Company, User.company_id == Company.company_id)
            .all()
        )

        # Format the results
        user_data = []
        for user, company in all_users:
            user_dict = user.to_dict()
            user_dict['company_name'] = company.company_name
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
        requested_user: User = User.query.filter_by(email=email).first()
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