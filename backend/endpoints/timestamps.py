from flask import Blueprint, request, jsonify
from models import db, User, TimeStamp
from datetime import datetime, timezone
from cmn_utils import print_exception

timestamps_bp = Blueprint('timestamps', __name__)

@timestamps_bp.route('/', methods=['POST'])
def create_timestamp():
    data = request.get_json()
    user_id = data.get('user_id')
    entered_by = data.get('entered_by')
    punch_type = data.get('punch_type')
    reporting_type = data.get('reporting_type')
    detail = data.get('detail')

    try:
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': f'User not found for id: {user_id}'}), 404

        entered_by_user = User.query.filter_by(id=entered_by).first()
        if not entered_by_user:
            return jsonify({'error': f'Entered by user not found for id: {entered_by}'}), 404

        punch_in_timestamp = datetime.now(timezone.utc)
        new_timestamp = TimeStamp(
            user_id=user.id,
            entered_by=entered_by_user.id,
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
def get_timestamps():
    try:
        timestamps = TimeStamp.query.all()
        timestamps_list = [timestamp.to_dict() for timestamp in timestamps]
        return jsonify(timestamps_list), 200

    except Exception as error:
        print_exception(error)
        return jsonify({'error': 'Internal server error'}), 500

@timestamps_bp.route('/punch_out', methods=['POST'])
def punch_out():
    data = request.get_json()
    user_id = data.get('user_id')
    entered_by = data.get('entered_by')
    reporting_type = data.get('reporting_type')
    detail = data.get('detail')

    try:
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': f'User not found for id: {user_id}'}), 404

        entered_by_user = User.query.filter_by(id=entered_by).first()
        if not entered_by_user:
            return jsonify({'error': f'Entered by user not found for id: {entered_by}'}), 404

        today = datetime.now(timezone.utc).date()
        start_of_day = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_of_day = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)

        timestamp = TimeStamp.query.filter(
            TimeStamp.user_id == user.id,
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
def check_punch_in_status():
    data = request.get_json()
    user_id = data.get('user_id')

    try:
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': f'User not found for id: {user_id}'}), 404

        today = datetime.now(timezone.utc).date()
        start_of_day = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_of_day = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)

        timestamp = TimeStamp.query.filter(
            TimeStamp.user_id == user.id,
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
def delete_timestamp(uuid):
    try:
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
def work_time_today():
    data = request.get_json()
    user_id = data.get('user_id')

    try:
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': f'User not found for id: {user_id}'}), 404

        # Get today's date range
        today = datetime.now(timezone.utc).date()
        start_of_day = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_of_day = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)

        # Fetch all timestamps for the user today
        timestamps = TimeStamp.query.filter(
            TimeStamp.user_id == user.id,
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
