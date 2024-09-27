from flask import Blueprint, request, jsonify
from models import Company, User, db  # Import your models
from cmn_utils import *

companies_blueprint = Blueprint('companies', __name__)

# Create company route
@companies_blueprint.route('/create-company', methods=['POST'])
def create_company():
    data = request.get_json()
    company_name = data.get('company_name')

    try:
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

# Update company route
@companies_blueprint.route('/update-company/<string:id>', methods=['PUT'])
def update_company(id):
    data = request.get_json()
    company_name = data.get('company_name')

    try:
        # Get the company using SQLAlchemy
        company = Company.query.get(id)
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
@companies_blueprint.route('/remove-company/<string:id>', methods=['PUT'])  # Changed to PUT for soft delete
def remove_company(id):
    try:
        # Soft delete company using SQLAlchemy
        company = Company.query.get(id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404

        company.is_active = False
        db.session.commit()

        return jsonify({'message': 'Company removed successfully', 'company': company.to_dict()}), 200

    except Exception as e:
        db.session.rollback()
        print_exception(e)
        return jsonify({'error': 'Server error'}), 500

# Get active companies route
@companies_blueprint.route('/active', methods=['GET'])
def get_active_companies():
    try:
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
def get_all_companies():
    try:
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

@companies_blueprint.route('/<string:company_id>/users')
def get_company_users(company_id):
    try:
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