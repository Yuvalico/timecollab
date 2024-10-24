from flask import Blueprint, request, jsonify
from models import db, User, TimeStamp
from datetime import datetime, timezone
from cmn_utils import print_exception, extract_jwt
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from cmn_defs import *

timestamps_bp = Blueprint('timestamps', __name__)

@timestamps_bp.route('/', methods=['POST'])
@jwt_required() 
def create_timestamp():
    try:
        data = request.get_json()
        user_email = data.get('user_email')
        entered_by = data.get('entered_by')
        punch_type = data.get('punch_type')
        reporting_type = data.get('reporting_type')
        detail = data.get('detail')

        current_user_email, user_permission, user_company_id = extract_jwt()

        user: User = User.query.filter_by(email=user_email).first()
        if not user:
            return jsonify({'error': f'User not found for email: {user_email}'}), 404

        entered_by_user: User = User.query.filter_by(email=entered_by).first()
        if not entered_by_user:
            return jsonify({'error': f'Entered by user not found for email: {entered_by}'}), 404

        punch_in_timestamp = datetime.now(timezone.utc)
        new_timestamp = TimeStamp(
            user_email=user.email,
            entered_by=entered_by_user.email,
            punch_type=punch_type,
            punch_in_timestamp=punch_in_timestamp,
            reporting_type=reporting_type,
            detail=detail
        )
        db.session.add(new_timestamp)
        db.session.commit()

        return jsonify({
            'message': 'Timestamp created successfully',
            'timestamp': new_timestamp.to_dict()
        }), 201

    except Exception as error:
        print_exception(error)
        db.session.rollback()
        return jsonify({'error': 'Server error'}), 500

@timestamps_bp.route('/', methods=['GET'])
@jwt_required() 
def get_timestamps():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        timestamps = TimeStamp.query.all()
        timestamps_list = [timestamp.to_dict() for timestamp in timestamps]
        return jsonify(timestamps_list), 200

    except Exception as error:
        print_exception(error)
        return jsonify({'error': 'Internal server error'}), 500

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

        user: User = User.query.filter_by(email=user_email).first()
        if not user:
            return jsonify({'error': f'User not found for id: {user_email}'}), 404

        entered_by_user = User.query.filter_by(email=entered_by).first()
        if not entered_by_user:
            return jsonify({'error': f'Entered by user not found for email: {entered_by}'}), 404

        today = datetime.now(timezone.utc).date()
        start_of_day = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_of_day = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)

        timestamp = TimeStamp.query.filter(
            TimeStamp.user_email == user.email,
            TimeStamp.punch_in_timestamp >= start_of_day,
            TimeStamp.punch_in_timestamp <= end_of_day,
            TimeStamp.punch_out_timestamp == None
        ).order_by(TimeStamp.punch_in_timestamp.desc()).first()

        if timestamp:
            timestamp.punch_out_timestamp = datetime.now(timezone.utc)
            timestamp.reporting_type = reporting_type
            timestamp.detail = detail
            db.session.commit()
            return jsonify({'message': 'Punched out successfully', 'timestamp': timestamp.to_dict()}), 200
        else:
            return jsonify({
                'error': 'No punch-in found for today. Please manually add a punch-in entry.',
                'action_required': 'manual_punch_in'
            }), 400

    except Exception as error:
        print_exception(error)
        db.session.rollback()
        return jsonify({'error': 'Server error'}), 500

@timestamps_bp.route('/punch_in_status', methods=['POST'])
@jwt_required() 
def check_punch_in_status():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        data = request.get_json()
        user_email = data.get('user_email')

        user: User = User.query.filter_by(email=user_email).first()
        if not user:
            return jsonify({'error': f'User not found for email: {user_email}'}), 404

        today = datetime.now(timezone.utc).date()
        start_of_day = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_of_day = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)

        timestamp = TimeStamp.query.filter(
            TimeStamp.user_email == user.email,
            TimeStamp.punch_in_timestamp >= start_of_day,
            TimeStamp.punch_in_timestamp <= end_of_day,
            TimeStamp.punch_out_timestamp == None
        ).order_by(TimeStamp.punch_in_timestamp.desc()).first()

        if timestamp:
            return jsonify({'has_punch_in': True}), 200
        else:
            return jsonify({'has_punch_in': False}), 200

    except Exception as error:
        print_exception(error)
        return jsonify({'error': 'Server error'}), 500

@timestamps_bp.route('/<uuid:uuid>', methods=['DELETE'])
@jwt_required() 
def delete_timestamp(uuid):
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        timestamp = TimeStamp.query.filter_by(uuid=uuid).first()
        if not timestamp:
            return jsonify({'error': 'Timestamp not found'}), 404

        db.session.delete(timestamp)
        db.session.commit()

        return jsonify({'message': 'Timestamp deleted successfully', 'timestamp': timestamp.to_dict()}), 200

    except Exception as error:
        print_exception(error)
        db.session.rollback()
        return jsonify({'error': 'Server error'}), 500

@timestamps_bp.route('/work_time_today', methods=['POST'])
@jwt_required() 
def work_time_today():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        data = request.get_json()
        user_email = data.get('user_email')

        user: User = User.query.filter_by(email=user_email).first()
        if not user:
            return jsonify({'error': f'User not found for email: {user_email}'}), 404

        # Get today's date range
        today = datetime.now(timezone.utc).date()
        start_of_day = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_of_day = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)

        # Fetch all timestamps for the user today
        timestamps = TimeStamp.query.filter(
            TimeStamp.user_email == user.email,
            TimeStamp.punch_in_timestamp >= start_of_day,
            TimeStamp.punch_in_timestamp <= end_of_day
        ).all()

        total_work_time = timedelta()

        for timestamp in timestamps:
            if timestamp.total_work_time:
                total_work_time += timestamp.total_work_time
            elif timestamp.punch_in_timestamp and not timestamp.punch_out_timestamp:
                # Include ongoing time
                total_work_time += datetime.now(timezone.utc) - timestamp.punch_in_timestamp

        # Convert total_work_time to a readable string
        total_seconds = int(total_work_time.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        total_time_str = f"{hours}h {minutes}m {seconds}s"

        return jsonify({'total_work_time': total_time_str}), 200

    except Exception as error:
        print_exception(error)
        return jsonify({'error': 'Server error'}), 500

@timestamps_bp.route('/getRange/<string:user_email>', methods=['GET'])
@jwt_required()
def get_timestamps_range(user_email):
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        requested_user: User = User.query.filter_by(email=user_email).first()
        print(f"Requested user email is: {user_email}")
        if not requested_user:
            return jsonify({'error': 'User not found'}), 404
        

        # Permission checks
        if user_permission == E_PERMISSIONS.net_admin:
            pass  # Net admin can access any user's data
        elif user_permission == E_PERMISSIONS.employer:
            if str(requested_user.company_id) != user_company_id:
                print(f"requested user company: {requested_user.company_id }\n requestor user company id: {user_company_id}")
                print(f"requested user company type: {type(requested_user.company_id )}\n requestor user company id: {type(user_company_id)}")
                print("unauthorized request. Not the same company")
                return jsonify({'error': 'Unauthorized access'}), 403
        elif user_permission == E_PERMISSIONS.employee:
            if current_user_email != user_email:
                print("unauthorized request. Not the same employee")
                return jsonify({'error': 'Unauthorized access'}), 403
        else:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Get start and end dates from query parameters
        # data = request.get_json()
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        if not start_date_str or not end_date_str:
            return jsonify({'error': 'Missing start_date or end_date'}), 400

        try:
            start_date = datetime.fromisoformat(start_date_str)
            end_date = datetime.fromisoformat(end_date_str)
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use ISO format (YYYY-MM-DD)'}), 400
        
        # Fetch timestamps for the user
        timestamps = TimeStamp.query.filter(
            TimeStamp.user_email == user_email,
            TimeStamp.punch_in_timestamp >= start_date,
            TimeStamp.punch_in_timestamp <= end_date
        ).all()

        timestamps_list = [timestamp.to_dict() for timestamp in timestamps]
        return jsonify(timestamps_list), 200

    except Exception as error:
        print_exception(error)
        return jsonify({'error': 'Internal server error'}), 500