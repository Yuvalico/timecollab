from flask import Blueprint, request, jsonify
from models import db, User, TimeStamp
from classes import UserRepository, TimeStampRepository
from classes.RC import RC 
from datetime import datetime, timezone
from cmn_utils import print_exception, extract_jwt, iso2datetime, datetime2iso, createRcjson
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from cmn_defs import *

timestamps_bp = Blueprint('timestamps', __name__)

user_repository = UserRepository.UserRepository(db)
timestamp_repository = TimeStampRepository.TimeStampRepository(db)

@timestamps_bp.route('/', methods=['POST'])
@jwt_required() 
def create_timestamp():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        data = request.get_json()
        user_email = data.get('user_email')
        entered_by_user = current_user_email
        punch_type = data.get('punch_type')
        reporting_type = data.get('reporting_type')
        detail = data.get('detail')
        punch_in = data.get("punch_in_timestamp")
        punch_out = data.get("punch_out_timestamp")
        
        if user_permission == E_PERMISSIONS.employee and current_user_email != user_email:
             return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED
         

        user: User|RC = user_repository.get_user_by_email(email=user_email)
        if isinstance (user, RC):
            return createRcjson(user)
        
        if user_permission == E_PERMISSIONS.employer and user_company_id != user.company_id:
             return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED

        new_timestamp = timestamp_repository.create_timestamp(user_email, entered_by_user, punch_type, punch_in, punch_out, reporting_type, detail)
        if isinstance(new_timestamp, RC):
            return jsonify({new_timestamp}), E_RC.RC_ERROR_DATABASE

        return jsonify({
            'message': 'Timestamp created successfully',
            'timestamp': new_timestamp.to_dict()
        }), E_RC.RC_SUCCESS

    except Exception as error:
        print_exception(error)
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE

@timestamps_bp.route('/', methods=['GET'])
@jwt_required() 
def get_timestamps():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        if user_permission != E_PERMISSIONS.net_admin:
             return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED
         
        timestamps = timestamp_repository.get_all_timestamps()
        timestamps_list = [timestamp.to_dict() for timestamp in timestamps]
        return jsonify(timestamps_list), E_RC.RC_OK

    except Exception as error:
        print_exception(error)
        return jsonify({'error': 'Internal server error'}), E_RC.RC_ERROR_DATABASE

@timestamps_bp.route('/', methods=['PUT'])
@jwt_required() 
def punch_out():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        data = request.get_json()
        user_email = data.get('user_email')
        entered_by = data.get('entered_by')
        reporting_type = data.get('reporting_type')
        detail = data.get('detail')

        if user_permission == E_PERMISSIONS.employee and current_user_email != user_email:
             return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED
         
        user: User|RC = user_repository.get_user_by_email(email=user_email)
        if isinstance (user, RC):
            return createRcjson(user)

        entered_by_user: User|RC= user_repository.get_user_by_email(email=entered_by)
        if isinstance (entered_by_user, RC):
            return createRcjson(entered_by_user)
        
        if user_permission == E_PERMISSIONS.employer and user_company_id != user.company_id:
             return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED

        rc : RC = timestamp_repository.punch_out(user.email, reporting_type, detail)
        return createRcjson(rc)
    
    except Exception as error:
        print_exception(error)
        db.session.rollback()
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE
    
@timestamps_bp.route('/<uuid:timestamp_uuid>', methods=['PUT'])
@jwt_required()
def edit(timestamp_uuid):
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        
        timestamp: TimeStamp|RC = timestamp_repository.get_timestamp_by_uuid(timestamp_uuid)
        if isinstance(timestamp, RC) :
            return createRcjson(timestamp)

        # Permission checks (similar to your get_timestamps_range function)
        if user_permission == E_PERMISSIONS.net_admin:
            pass  # Net admin can edit any timestamp
        elif user_permission == E_PERMISSIONS.employer:
            if str(timestamp.user.company_id) != user_company_id:
                return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED
        elif user_permission == E_PERMISSIONS.employee:
            if current_user_email != timestamp.user_email:
                return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED
        else:
            return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED

        data = request.get_json()

        punch_in_timestamp = data.get('punch_in_timestamp')
        punch_out_timestamp = data.get('punch_out_timestamp')
        punch_type = data.get('punch_type')
        detail = data.get('detail')
        reporting_type = data.get('reporting_type')
        
        rc: RC = timestamp_repository.edit_timestamp(timestamp, current_user_email, punch_type, punch_in_timestamp, punch_out_timestamp, reporting_type, detail)
        
        return createRcjson(rc)
    
    except Exception as error:
        print_exception(error)
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE

@timestamps_bp.route('/punch_in_status', methods=['POST'])
@jwt_required() 
def check_punch_in_status():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        data = request.get_json()
        user_email = data.get('user_email')

        if user_permission == E_PERMISSIONS.employee and current_user_email != user_email:
             return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED
         
        user: User|RC = user_repository.get_user_by_email(email=user_email)
        if isinstance (user, RC):
            return createRcjson(user)
        
        if user_permission == E_PERMISSIONS.employer and user_company_id != user.company_id:
             return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED

        answer: bool|RC= timestamp_repository.check_punch_in_status(current_user_email)
        if isinstance(answer, RC):
            return createRcjson(answer)
        
        elif answer:
            return jsonify({'has_punch_in': True}), E_RC.RC_OK
        else:
            return jsonify({'has_punch_in': False}), E_RC.RC_OK

    except Exception as error:
        print_exception(error)
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE

@timestamps_bp.route('/<uuid:uuid>', methods=['DELETE'])
@jwt_required() 
def delete_timestamp(uuid):
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        timestamp = timestamp_repository.get_timestamp_by_uuid(uuid)
        if isinstance(timestamp, RC):
            return createRcjson(timestamp)
        
        if not timestamp:
            return jsonify({'error': 'Timestamp not found'}), E_RC.RC_NOT_FOUND

        if user_permission == E_PERMISSIONS.employee and current_user_email != timestamp.user.email:
             return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED
         
        if user_permission == E_PERMISSIONS.employer and user_company_id != timestamp.user.company_id:
             return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED
         
        rc: RC = timestamp_repository.delete_timestamp(uuid)
        return createRcjson(rc)
        
    except Exception as error:
        print_exception(error)
        db.session.rollback()
        return jsonify({'error': 'Server error'}), E_RC.RC_ERROR_DATABASE


@timestamps_bp.route('/getRange/<string:user_email>', methods=['GET'])
@jwt_required()
def get_timestamps_range(user_email):
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        requested_user: User|RC = user_repository.get_user_by_email(email=user_email)
        if isinstance (requested_user,RC):
            return createRcjson(requested_user)
        
        if user_permission == E_PERMISSIONS.net_admin:
            pass  # Net admin can access any user's data
        elif user_permission == E_PERMISSIONS.employer:
            if str(requested_user.company_id) != user_company_id:
                return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED
            
        elif user_permission == E_PERMISSIONS.employee:
            if current_user_email != user_email:
                print("unauthorized request. Not the same employee")
                return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED
            
        else:
            return jsonify({'error': 'Unauthorized access'}), E_RC.RC_UNAUTHORIZED
        
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        timestamps = timestamp_repository.get_range(start_date_str, end_date_str, requested_user.email)
        if isinstance(timestamps, RC):
            return createRcjson(timestamps)
        
        timestamps_list = [timestamp.to_dict() for timestamp in timestamps]
        return jsonify(timestamps_list), E_RC.RC_OK

    except Exception as error:
        print_exception(error)
        return jsonify({'error': 'Internal server error'}), E_RC.RC_ERROR_DATABASE