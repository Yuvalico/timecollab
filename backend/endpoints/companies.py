from flask import Blueprint, request, jsonify
from models import Company, User, db  # Import your models
from cmn_utils import *
from cmn_defs import *
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

companies_blueprint = Blueprint('companies', __name__)

# Create company route
@companies_blueprint.route('/create-company', methods=['POST'])
@jwt_required() 
def create_company():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        if E_PERMISSIONS.to_enum(user_permission) > E_PERMISSIONS.net_admin:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        data = request.get_json()
        company_name = data.get('company_name')

        # Check if company already exists using SQLAlchemy
        existing_company = Company.query.filter_by(company_name=company_name).first()
        if existing_company:
            return jsonify({'error': 'Company already exists'}), 400

        # Create new company object
        new_company = Company(company_name=company_name)

        # Add and commit using SQLAlchemy
        db.session.add(new_company)
        db.session.commit()

        return jsonify({'message': 'Company created successfully', 'company': new_company.to_dict()}), 201

    except Exception as e:
        db.session.rollback()  # Rollback in case of an error
        print_exception(e)  # Assuming you have a print_exception function
        return jsonify({'error': 'Server error'}), 500

@companies_blueprint.route('/update-company', methods=['PUT'])
@jwt_required() 
def update_company():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        if E_PERMISSIONS.to_enum(user_permission) > E_PERMISSIONS.net_admin:
            return jsonify({'error': 'Unauthorized access'}), 403
         
        data = request.get_json()
        company_id = data.get('company_id')  # Get company_id from the request body
        company_name = data.get('company_name')

        # Get the company using SQLAlchemy
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404

        # Update company name
        company.company_name = company_name

        # Commit changes using SQLAlchemy
        db.session.commit()

        return jsonify({'message': 'Company updated successfully', 'company': company.to_dict()}), 200

    except Exception as e:
        db.session.rollback()
        print_exception(e)
        return jsonify({'error': 'Server error'}), 500

# "Remove" company route (soft delete)
@companies_blueprint.route('/remove-company/<string:company_id>', methods=['PUT'])
@jwt_required() 
def remove_company(company_id):
    # data = request.get_json()
    # company_id = data.get('company_id')  # Get company_id from the request body
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        if E_PERMISSIONS.to_enum(user_permission) > E_PERMISSIONS.net_admin:
            return jsonify({'error': 'Unauthorized access'}), 403 
        # Soft delete company using SQLAlchemy
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404

        company.is_active = False
        db.session.commit()

        return jsonify({'message': 'Company removed successfully', 'company': company.to_dict()}), 200

    except Exception as e:
        db.session.rollback()
        print_exception(e)  # Assuming you have a print_exception function
        return jsonify({'error': 'Server error'}), 500

# Get active companies route
@companies_blueprint.route('/active', methods=['GET'])
@jwt_required() 
def get_active_companies():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        if E_PERMISSIONS.to_enum(user_permission) > E_PERMISSIONS.net_admin:
            return jsonify({'error': 'Unauthorized access'}), 403 

        # Query active companies using SQLAlchemy and join with users to get the admin
        active_companies = (
            db.session.query(Company)
            .filter_by(is_active=True)
            .outerjoin(User, (User.company_id == Company.company_id) & (User.role == 'admin'))
            .all()
        )

        # Format the results
        company_data = []
        for company in active_companies:
            company_dict = company.to_dict()
            admin_user = company.users[0] if company.users else None  # Get the first admin user or None
            company_dict['admin_user'] = admin_user.to_dict() if admin_user else None
            company_data.append(company_dict)

        return jsonify(company_data), 200

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Internal server error'}), 500

# Get all companies route
@companies_blueprint.route('/', methods=['GET'])
@jwt_required() 
def get_all_companies():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        if E_PERMISSIONS.to_enum(user_permission) > E_PERMISSIONS.net_admin:
            return jsonify({'error': 'Unauthorized access'}), 403 
        
        # Query all companies using SQLAlchemy and join with users to get the admin
        all_companies = (
            db.session.query(Company)
            .outerjoin(User, (User.company_id == Company.company_id) & (User.role == 'admin'))
            .all()
        )

        # Format the results
        company_data = []
        for company in all_companies:
            company_dict = company.to_dict()
            admin_user = company.users[0] if company.users else None
            company_dict['admin_user'] = admin_user.to_dict() if admin_user else None
            company_data.append(company_dict)

        return jsonify(company_data), 200

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Internal server error'}), 500

@companies_blueprint.route('<string:company_id>/users', methods=['GET'])
@jwt_required() 
def get_company_users(company_id):
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        
        # Query the company by its ID
        company = Company.query.get(company_id)

        # Check if the company exists
        if not company:
            return jsonify({'error': 'Company not found'}), 404

        # Get all users associated with the company
        users = User.query.filter_by(company_id=company_id).all()

        # Convert the users to dictionaries and include them in the response
        user_data = [user.to_dict() for user in users]
        return jsonify(user_data), 200

    except Exception as e:
        # Handle any unexpected errors
        return jsonify({'error': str(e)}), 500

@companies_blueprint.route('/<string:company_id>', methods=['GET'])
@jwt_required() 
def get_company_details(company_id):
    try:
        # Get the identity of the current user from the JWT
        current_user_email, user_permission, user_company_id = extract_jwt()

        # Query the company by ID (using the company_id from the URL path)
        company: Company = Company.query.filter_by(company_id=company_id).first()

        if not company:
            return jsonify({'error': 'Company not found'}), 404

        company_dict = company.to_dict()
        if user_permission == E_PERMISSIONS.net_admin:
            return jsonify(company_dict), 200
        
        # Check if the current user is an employee or the employer of the company
        if user_company_id == company_id:
            if user_permission == 1:  # Employer
                return jsonify(company_dict), 200
            else:  # Employee
                return jsonify({'company_name': company.company_name}), 200
        else:
            return jsonify({'error': 'Unauthorized access'}), 403 

    except Exception as e:
        return jsonify({'error': str(e)}), 500