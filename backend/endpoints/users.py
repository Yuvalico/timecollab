from flask import Blueprint, request, jsonify, current_app
from models import User, Company, db  
import bcrypt
from cmn_utils import *

users_blueprint = Blueprint('users', __name__)

# Permission maps
permission_map_to_int = {
    'Net Admin': 0,
    'Employer': 1,
    'Employee': 2,
}

permission_map_to_str = {
    0: 'Net Admin',
    1: 'Employer',
    2: 'Employee',
}

# Create user route
@users_blueprint.route('/create-user', methods=['POST'])
def create_user():
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

    try:
        permission_int = permission_map_to_int.get(permission)
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
@users_blueprint.route('/update-user/<uuid:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    mobile_phone = data.get('mobile_phone')
    email = data.get('email')
    role = data.get('role')
    permission = data.get('permission')
    salary = data.get('salary')
    work_capacity = data.get('work_capacity')

    try:
        permission_int = permission_map_to_int.get(permission)
        if permission_int is None:
            return jsonify({'error': 'Invalid permission type'}), 400

        # Get the user using SQLAlchemy
        user = User.query.get(id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Update user attributes
        user.first_name = first_name
        user.last_name = last_name
        user.mobile_phone = mobile_phone
        user.email = email
        user.role = role
        user.permission = permission_int
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
@users_blueprint.route('/remove-user/<uuid:id>', methods=['PUT'])
def remove_user(id):
    try:
        # Soft delete user using SQLAlchemy
        user = User.query.get(id)
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
def get_active_users():
    try:
        # Query active users using SQLAlchemy and join with companies
        active_users = (
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
            user_dict['permission'] = permission_map_to_str.get(user.permission, 'Unknown')
            user_data.append(user_dict)

        return jsonify(user_data), 200

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Internal server error'}), 500

# Get all users route
@users_blueprint.route('/', methods=['GET'])
def get_all_users():
    try:
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

@users_blueprint.route('/get-user-by-email/<string:email>', methods=['GET'])
def get_user_by_email(email):
    try:
        # Query the user by email
        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify(user.to_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500