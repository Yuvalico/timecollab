from flask import Blueprint, request, jsonify, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
from cmn_utils import *


companies_blueprint = Blueprint('companies', __name__)

# Create company route
@companies_blueprint.route('/create-company', methods=['POST'])
def create_company():
    data = request.get_json()
    company_name = data.get('company_name')

    conn = get_db_connection(current_app.config)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Check if company already exists
        cursor.execute('SELECT * FROM companies WHERE company_name = %s', (company_name,))
        existing_company = cursor.fetchone()
        if existing_company:
            return jsonify({'error': 'Company already exists'}), 400

        # Insert new company
        cursor.execute('INSERT INTO companies (company_name) VALUES (%s) RETURNING *', (company_name,))
        new_company = cursor.fetchone()
        conn.commit()  # Commit the changes

        return jsonify({'message': 'Company created successfully', 'company': new_company}), 201

    except (Exception, psycopg2.Error) as error:
        print_exception(error)
        return jsonify({'error': 'Server error'}), 500

    finally:
        cursor.close()
        conn.close()

# Update company route
@companies_blueprint.route('/update-company/<string:id>', methods=['PUT'])
def update_company(id):
    data = request.get_json()
    company_name = data.get('company_name')

    conn = get_db_connection(current_app.config)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Update company
        cursor.execute('UPDATE companies SET company_name = %s WHERE company_id = %s RETURNING *', (company_name, id))
        updated_company = cursor.fetchone()
        conn.commit()

        if not updated_company:
            return jsonify({'error': 'Company not found'}), 404

        return jsonify({'message': 'Company updated successfully', 'company': updated_company}), 200

    except (Exception, psycopg2.Error) as error:
        print_exception(error)
        return jsonify({'error': 'Server error'}), 500

    finally:
        cursor.close()
        conn.close()

# "Remove" company route (soft delete)
@companies_blueprint.route('/remove-company/<string:id>', methods=['PUT'])
def remove_company(id):
    conn = get_db_connection(current_app.config)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Soft delete company
        cursor.execute('UPDATE companies SET is_active = false WHERE company_id = %s RETURNING *', (id,))
        removed_company = cursor.fetchone()
        conn.commit()

        if not removed_company:
            return jsonify({'error': 'Company not found'}), 404

        return jsonify({'message': 'Company removed successfully', 'company': removed_company}), 200

    except (Exception, psycopg2.Error) as error:
        print_exception(error)
        return jsonify({'error': 'Server error'}), 500

    finally:
        cursor.close()
        conn.close()

# Get active companies route
@companies_blueprint.route('/active', methods=['GET'])
def get_active_companies():
    conn = get_db_connection(current_app.config)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute('''
            SELECT c.company_id, c.company_name, 
            (SELECT CONCAT(u.first_name, ' ', u.last_name)
             FROM users u 
             WHERE u.company_id = c.company_id AND u.role = 'admin'
             LIMIT 1) AS admin_user
            FROM companies c
            WHERE c.is_active = true
        ''')
        active_companies = cursor.fetchall()

        return jsonify(active_companies), 200

    except (Exception, psycopg2.Error) as error:
        print_exception(error)
        return jsonify({'error': 'Internal server error'}), 500

    finally:
        cursor.close()
        conn.close()

# Get all companies route
@companies_blueprint.route('/', methods=['GET'])
def get_all_companies():
    conn = get_db_connection(current_app.config)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute('''
            SELECT c.company_id, c.company_name, 
            (SELECT CONCAT(u.first_name, ' ', u.last_name)
             FROM users u 
             WHERE u.company_id = c.company_id AND u.role = 'admin'
             LIMIT 1) AS admin_user
            FROM companies c
        ''')
        all_companies = cursor.fetchall()

        return jsonify(all_companies), 200

    except (Exception, psycopg2.Error) as error:
        print_exception(error)
        return jsonify({'error': 'Internal server error'}), 500

    finally:
        cursor.close()
        conn.close()