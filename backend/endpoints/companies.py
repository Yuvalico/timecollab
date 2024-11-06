from flask import Blueprint, request, jsonify
from models import Company, User, db  # Import your models
from classes import CompanyRepository, UserRepository
from classes.RC import RC
from cmn_utils import *
from cmn_defs import *
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

companies_blueprint = Blueprint('companies', __name__)
company_repository = CompanyRepository.CompanyRepository(db)
user_repository = UserRepository.UserRepository(db)

# Create company route
@companies_blueprint.route('/create-company', methods=['POST'])
@jwt_required() 
def create_company():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        if E_PERMISSIONS.to_enum(user_permission) > E_PERMISSIONS.net_admin:
            return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED
        
        data = request.get_json()
        company_name = data.get('companyName')

        # Check if company already exists using SQLAlchemy
        existing_company = company_repository.get_company_by_name(company_name=company_name)
        if not isinstance(existing_company, RC):
            return jsonify({'error': 'Company already exists'}), E_RC.RC_INVALID_INPUT

        # Create new company object
        rc: RC = company_repository.create_company(company_name=company_name)
        return createRcjson(rc)
        
    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE

@companies_blueprint.route('/update-company/', methods=['PUT'])
@jwt_required() 
def update_company():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        if E_PERMISSIONS.to_enum(user_permission) > E_PERMISSIONS.net_admin:
            return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED
         
        data = request.get_json()
        company_id = data.get('company_id')  # Get company_id from the request body
        company_name = data.get('company_name')

        # Get the company using SQLAlchemy
        company: Company | RC = company_repository.get_company_by_id(company_id)
        if isinstance(company, RC):
            return createRcjson(company)

        # Update company name
        rc: RC = company_repository.update_company(company_name)
        return createRcjson(rc)
    
    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE

# "Remove" company 
@companies_blueprint.route('/remove-company/<string:company_id>', methods=['PUT'])
@jwt_required() 
def remove_company(company_id):
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        if E_PERMISSIONS.to_enum(user_permission) > E_PERMISSIONS.net_admin:
            return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED 
        # Soft delete company using SQLAlchemy
        company = company_repository.get_company_by_id(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), E_RC.RC_NOT_FOUND

        rc: RC = company_repository.delete_company(company)
        
        return createRcjson(rc)
    
    except Exception as e:
        print_exception(e) 
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE

# Get active companies route
@companies_blueprint.route('/active', methods=['GET'])
@jwt_required() 
def get_active_companies():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        if E_PERMISSIONS.to_enum(user_permission) > E_PERMISSIONS.net_admin:
            return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED 

        # Query active companies using SQLAlchemy and join with users to get the admin
        active_companies = company_repository.get_all_active_companies()
        
        # Format the results
        company_data = []
        for company in active_companies:
            company_dict = company.to_dict()
            admins = company_repository.get_company_admins(company.company_id)
            company_dict['admin_user'] = admins[0].to_dict() if len(admins) else None
            company_data.append(company_dict)

        return jsonify(company_data), E_RC.RC_OK

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Internal server error'}), E_RC.RC_ERROR_DATABASE

# Get all companies route
@companies_blueprint.route('/', methods=['GET'])
@jwt_required() 
def get_all_companies():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        if E_PERMISSIONS.to_enum(user_permission) > E_PERMISSIONS.net_admin:
            return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED 
        
        # Query all companies using SQLAlchemy and join with users to get the admin
        all_companies = company_repository.get_all_companies()

        # Format the results
        company_data = []
        for company in all_companies:
            company_dict = company.to_dict()
            admins = company_repository.get_company_admins(company.company_id)
            company_dict['admin_user'] = admins[0].to_dict() if len(admins) else None
            company_data.append(company_dict)

        return jsonify(company_data), E_RC.RC_OK

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Internal server error'}), E_RC.RC_ERROR_DATABASE

@companies_blueprint.route('<string:company_id>/users', methods=['GET'])
@jwt_required() 
def get_company_users(company_id):
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        
        company = company_repository.get_company_by_id(company_id=company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), E_RC.RC_NOT_FOUND

        users = company_repository.get_company_users(company_id=company_id)
        user_data = [user.to_dict() for user in users]
        return jsonify(user_data), E_RC.RC_OK

    except Exception as e:
        print_exception(e)
        return jsonify({'error': str(e)}), E_RC.RC_ERROR_DATABASE

@companies_blueprint.route('/<string:company_id>', methods=['GET'])
@jwt_required() 
def get_company_details(company_id):
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        company: Company = company_repository.get_company_by_id(company_id=company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), E_RC.RC_NOT_FOUND

        company_dict = company.to_dict()
        if user_permission == E_PERMISSIONS.net_admin:
            return jsonify(company_dict), E_RC.RC_OK
        
        if user_company_id == company_id:
            if user_permission == 1:  # Employer
                return jsonify(company_dict), E_RC.RC_OK
            else:
                return jsonify({'company_name': company.company_name}), E_RC.RC_OK
        else:
            return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED 

    except Exception as e:
        print_exception(e)
        return jsonify({'error': str(e)}), E_RC.RC_ERROR_DATABASE
    
@companies_blueprint.route('/<string:company_id>/admins', methods=['GET'])
@jwt_required()
def get_company_admins(company_id):
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        company = company_repository.get_company_by_id(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), E_RC.RC_NOT_FOUND

        if user_permission == E_PERMISSIONS.employee:
            return jsonify({'error': 'Unauthorized to access this information'}), E_RC.RC_UNAUTHORIZED

        if user_permission == E_PERMISSIONS.employer and user_company_id != company_id:
            return jsonify({'error': 'Unauthorized to access this information'}), E_RC.RC_UNAUTHORIZED

        admins = company_repository.get_company_admins(company_id)

        admin_data = [admin.to_dict() for admin in admins]
        return jsonify(admin_data), E_RC.RC_OK

    except Exception as e:
        print_exception(e)
        return jsonify({'error': str(e)}), E_RC.RC_ERROR_DATABASE
    
    
@companies_blueprint.route('/<string:company_id>/name', methods=['GET'])
@jwt_required()
def get_company_name_by_id(company_id):
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        company = company_repository.get_company_by_id(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), E_RC.RC_NOT_FOUND

        if user_permission == E_PERMISSIONS.employee and user_company_id != company_id:
            return jsonify({'error': 'Unauthorized to access this information'}), E_RC.RC_UNAUTHORIZED

        if user_permission == E_PERMISSIONS.employer and user_company_id != company_id:
            return jsonify({'error': 'Unauthorized to access this information'}), E_RC.RC_UNAUTHORIZED

        return jsonify({'company_name': company.company_name}), E_RC.RC_OK

    except Exception as e:
        print_exception(e)
        return jsonify({'error': str(e)}), E_RC.RC_ERROR_DATABASE