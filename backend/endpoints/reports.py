from flask import Blueprint, request, jsonify
from models import db, User, TimeStamp, Company
from datetime import datetime, timezone, timedelta
from cmn_utils import print_exception, extract_jwt, calculate_work_capacity, format_hours_to_hhmm
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from cmn_defs import *
import calendar

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/generate-user', methods=['GET'])
@jwt_required()
def generate_user_report():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        claims = get_jwt()

        company_id = request.args.get('company_id')
        user_email = request.args.get('user_email')
        date_range_type = request.args.get('dateRangeType')
        selected_year = request.args.get('year')
        selected_month = request.args.get('month')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        requested_user: User = User.query.get(current_user_email)
        # Validate company_id if provided
        if company_id:
            company = Company.query.get(company_id)
            if not company:
                return jsonify({'error': 'Company not found'}), 404

        # Permission check for accessing other user's reports
        if user_email and user_email != current_user_email \
                and user_permission == E_PERMISSIONS.employee:
            return jsonify(
                {'error': 'Unauthorized to access this report'}), 403

        if E_PERMISSIONS.employer == user_permission and (
                user_company_id != company_id
                or str(requested_user.company_id) != str(user_company_id)):
            return jsonify(
                {'error': 'Unauthorized to access this report'}), 403
        
        # Determine date range
        if date_range_type == 'monthly':
            if not selected_year or not selected_month:
                return jsonify({
                    'error': 'Year and month are required for monthly reports'
                }), 400

            year = int(selected_year)
            month = int(selected_month)
            start_date = datetime(year, month, 1, tzinfo=timezone.utc)
            end_date = datetime(year, month, calendar.monthrange(year, month)[1], tzinfo=timezone.utc)
        elif date_range_type == 'custom':
            if not start_date_str or not end_date_str:
                return jsonify({
                    'error':
                    'Start and end dates are required for custom reports'
                }), 400
            try:
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00') if start_date_str.endswith('Z') else start_date_str)
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00') if end_date_str.endswith('Z') else end_date_str)

            except ValueError:
                return jsonify({'error': 'Invalid date format'}), 400
        else:
            return jsonify({'error': 'Invalid date range type'}), 400

        # Query TimeStamps
        query = TimeStamp.query.filter(TimeStamp.punch_in_timestamp >=
                                       start_date,
                                       TimeStamp.punch_in_timestamp <= end_date)

        if user_email:
            query = query.filter_by(user_email=user_email)
        elif company_id:
            query = query.join(User).filter(User.company_id == company_id)

        time_stamps = query.all()

        # Generate the report data
        report = generate_user_report_data(time_stamps, start_date, end_date)
        return jsonify(report)

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Failed to generate report'}), 500

@reports_bp.route('/generate_company', methods=['GET'])
@jwt_required()
def generate_company_summary_report():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        claims = get_jwt()

        company_id = request.args.get('company_id')
        date_range_type = request.args.get('dateRangeType')
        selected_year = request.args.get('year')
        selected_month = request.args.get('month')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        # Validate company_id
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400

        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404

        # Permission check
        if user_permission == E_PERMISSIONS.employee:
            return jsonify({'error': 'Unauthorized to access this report'}), 403

        if E_PERMISSIONS.employer == user_permission and str(user_company_id) != str(company_id):
            return jsonify({'error': 'Unauthorized to access this report'}), 403

        # Determine date range
        if date_range_type == 'monthly':
            if not selected_year or not selected_month:
                return jsonify({'error': 'Year and month are required for monthly reports'}), 400

            year = int(selected_year)
            month = int(selected_month)
            start_date = datetime(year, month, 1, tzinfo=timezone.utc)
            end_date = datetime(year, month, calendar.monthrange(year, month)[1], tzinfo=timezone.utc)
            
        elif date_range_type == 'custom':
            if not start_date_str or not end_date_str:
                return jsonify({'error': 'Start and end dates are required for custom reports'}), 400
            try:
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid date format'}), 400
        else:
            return jsonify({'error': 'Invalid date range type'}), 400

        # Query TimeStamps
        query = TimeStamp.query.filter(TimeStamp.punch_in_timestamp >= start_date,
                                        TimeStamp.punch_in_timestamp <= end_date).join(User, TimeStamp.user_email == User.email)\
                                            .filter(User.company_id == company_id)
        time_stamps = query.all()

        # Generate the company summary report data
        report = generate_company_summary_data(time_stamps, start_date, end_date)
        return jsonify(report)

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Failed to generate report'}), 500
    
def generate_user_report_data(time_stamps, start_date, end_date):
    if not time_stamps:
        return {}  # Return empty object if no time stamps found

    user: User = time_stamps[0].user
    employee_name = user.first_name + " " + user.last_name
    dates_worked = []
    dates_missed = []
    total_hours_worked = 0
    daily_breakdown = []
    salary = float(user.salary or 0)  # Get salary, handle potential None, convert to float

    current_date = start_date
    while current_date <= end_date:
        daily_hours = 0
        for ts in time_stamps:
            if ts.punch_in_timestamp.date() == current_date.date():
                dates_worked.append(current_date.strftime('%Y-%m-%d'))
                daily_hours += ts.total_work_time or 0
                break
        else:
            dates_missed.append(current_date.strftime('%Y-%m-%d'))

        total_hours_worked += daily_hours
        daily_breakdown.append({
            "date": current_date.strftime('%Y-%m-%d'),
            "hoursWorked": format_hours_to_hhmm(daily_hours)
        })
        current_date += timedelta(days=1)

    total_payment_required = (total_hours_worked / 3600.0) * salary  # Calculate payment (salary is already a float)

    report = {
        "employeeName": employee_name,
        "datesWorked": dates_worked,
        "datesMissed": dates_missed,
        "totalHoursWorked": format_hours_to_hhmm(total_hours_worked),
        "totalPaymentRequired": round(total_payment_required, 2),
        "dailyBreakdown": daily_breakdown,
        "userDetails": {  # Add user details section
            "email": user.email,
            "role": user.role,
            "phone": user.mobile_phone,
            "salary": salary,  # Use the float value directly
            "workCapacity": float(user.work_capacity or 0)  # Handle potential None, convert to float
        }
    }

    return report

def generate_company_summary_data(time_stamps, start_date, end_date):
    if not time_stamps:
        return {}  # Return empty object if no time stamps found

    # Group time stamps by user
    time_stamps_by_user = {}
    for ts in time_stamps:
        if ts.user_email not in time_stamps_by_user:
            time_stamps_by_user[ts.user_email] = []
        time_stamps_by_user[ts.user_email].append(ts)

    report = []
    for user_email, user_time_stamps in time_stamps_by_user.items():
        user = user_time_stamps[0].user
        employee_name = user.first_name + " " + user.last_name
        dates_worked = set()  # Use a set to avoid duplicate dates
        total_hours_worked = 0
        salary = float(user.salary or 0)

        for ts in user_time_stamps:
            dates_worked.add(ts.punch_in_timestamp.strftime('%Y-%m-%d'))
            total_hours_worked += ts.total_work_time or 0

        days_worked = len(dates_worked)
        total_days = (end_date - start_date).days + 1
        days_not_worked = total_days - days_worked
        total_payment_required = (total_hours_worked / 3600.0) * salary

        report.append({
            "employeeName": employee_name,
            "userDetails": {
                "email": user.email,
                "role": user.role,
                "phone": user.mobile_phone,
                "salary": salary,
                "workCapacity": calculate_work_capacity(user, start_date, end_date)  # Calculate work capacity
            },
            "daysWorked": days_worked,
            "daysNotWorked": days_not_worked,
            "totalHoursWorked": format_hours_to_hhmm(total_hours_worked),
            "totalPaymentRequired": round(total_payment_required, 2),
        })

    return report