from flask import Blueprint, request, jsonify, current_app
import psycopg2 
import psycopg2.extras
from psycopg2.extras import RealDictCursor
import bcrypt
from cmn_utils import *
psycopg2.extras.register_uuid() 

users_blueprint = Blueprint('users', __name__)

# Permission maps (same as in your JavaScript)
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

        conn = get_db_connection(current_app.config)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Check if user already exists
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            return jsonify({'error': 'User already exists'}), 400

        # Get the company_id
        cursor.execute('SELECT company_id FROM companies WHERE company_name = %s', (company_name,))
        company_result = cursor.fetchone()
        if not company_result:
            return jsonify({'error': 'Company not found'}), 404
        company_id = company_result['company_id']

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert new user
        cursor.execute('''
            INSERT INTO users (email, first_name, last_name, company_id, role, permission, pass_hash, is_active, salary, work_capacity)
            VALUES (%s, %s, %s, %s, %s, %s, %s, true, %s, %s) RETURNING *
        ''', (email, first_name, last_name, company_id, role, permission_int, hashed_password.decode('utf-8'), salary, work_capacity))
        new_user = cursor.fetchone()
        conn.commit()

        return jsonify({'message': 'User registered successfully', 'user': new_user}), 201

    except (Exception, psycopg2.Error) as error:
        print_exception(error)
        return jsonify({'error': 'Server error'}), 500

    finally:
        cursor.close()
        conn.close()

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

        conn = get_db_connection(current_app.config)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Update the user
        cursor.execute('''
            UPDATE users 
            SET first_name = %s, last_name = %s, mobile_phone = %s, email = %s, role = %s, permission = %s, salary = %s, work_capacity = %s 
            WHERE id = %s RETURNING *
        ''', (first_name, last_name, mobile_phone, email, role, permission_int, salary, work_capacity, id))

        updated_user = cursor.fetchone()
        conn.commit()

        if not updated_user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({'message': 'User updated successfully', 'user': updated_user}), 200

    except (Exception, psycopg2.Error) as error:
        print_exception(error)
        return jsonify({'error': 'Server error'}), 500

    finally:
        cursor.close()
        conn.close()

# Remove user route (soft delete)
@users_blueprint.route('/remove-user/<uuid:id>', methods=['PUT'])
def remove_user(id):
    conn = get_db_connection(current_app.config)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Soft delete user
        cursor.execute('UPDATE users SET is_active = false WHERE id = %s RETURNING *', (id,))
        removed_user = cursor.fetchone()
        conn.commit()

        if not removed_user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({'message': 'User removed successfully', 'user': removed_user}), 200

    except (Exception, psycopg2.Error) as error:
        print_exception(error)
        return jsonify({'error': 'Server error'}), 500

    finally:
        cursor.close()
        conn.close()

# Get active users route
@users_blueprint.route('/active', methods=['GET'])
def get_active_users():
    conn = get_db_connection(current_app.config)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute('''
            SELECT u.id, u.first_name, u.last_name, u.mobile_phone, u.email, u.company_id, c.company_name, u.role, u.permission, u.is_active, u.salary, u.work_capacity
            FROM users u
            JOIN companies c ON u.company_id = c.company_id
            WHERE u.is_active = true
        ''')
        active_users = cursor.fetchall()

        # Map permission integers to strings
        users_with_mapped_permissions = []
        for user in active_users:
            user['permission'] = permission_map_to_str.get(user['permission'], 'Unknown')
            users_with_mapped_permissions.append(user)

        return jsonify(users_with_mapped_permissions), 200

    except (Exception, psycopg2.Error) as error:
        print_exception(error)
        return jsonify({'error': 'Internal server error'}), 500

    finally:
        cursor.close()
        conn.close()

# Get all users route
@users_blueprint.route('/', methods=['GET'])
def get_all_users():
    conn = get_db_connection(current_app.config)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute('''
            SELECT u.id, u.first_name, u.last_name, u.mobile_phone, u.email, u.company_id, c.company_name, u.role, u.permission, u.is_active, u.salary, u.work_capacity
            FROM users u
            JOIN companies c ON u.company_id = c.company_id
        ''')
        all_users = cursor.fetchall()

        return jsonify(all_users), 200

    except (Exception, psycopg2.Error) as error:
        print_exception(error)
        return jsonify({'error': 'Internal server error'}), 500

    finally:
        cursor.close()
        conn.close()
