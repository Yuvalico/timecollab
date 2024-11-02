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
                if end_date < start_date:
                    return jsonify({'error': 'Start date must earlier than end date'}), 400
                
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
        else:
            return jsonify({'error': 'Invalid user entered'}), 400
        # elif company_id:
        #     query = query.join(User).filter(User.company_id == company_id)

        time_stamps = query.all()

        # Generate the report data
        report = generate_user_report_data(user_email, time_stamps, start_date, end_date)
        return jsonify(report)

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Failed to generate report'}), 500

@reports_bp.route('/generate-company', methods=['GET'])
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
        report = generate_company_summary_data(company_id, time_stamps, start_date, end_date)
        return jsonify(report)

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Failed to generate report'}), 500

@reports_bp.route('/generate-company-overview', methods=['GET'])
@jwt_required()
def generate_company_overview_report():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        # Permission check (only for netadmins)
        if user_permission != E_PERMISSIONS.net_admin:
            return jsonify({'error': 'Unauthorized to access this report'}), 403

        date_range_type = request.args.get('dateRangeType')
        selected_year = request.args.get('year')
        selected_month = request.args.get('month')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

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
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00') if start_date_str.endswith('Z') else start_date_str)
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00') if end_date_str.endswith('Z') else end_date_str)
            except ValueError:
                return jsonify({'error': 'Invalid date format'}), 400
        else:
            return jsonify({'error': 'Invalid date range type'}), 400

        # Query all companies
        companies = Company.query.filter_by(is_active=True).all()  # Add is_active filter

        report = []
        for company in companies:
            # Query TimeStamps for the current company
            query = TimeStamp.query.filter(TimeStamp.punch_in_timestamp >= start_date,
                                            TimeStamp.punch_in_timestamp <= end_date) \
                                  .join(User, TimeStamp.user_email == User.email) \
                                  .filter(User.company_id == company.company_id)
            time_stamps = query.all()

            # Generate the company overview data
            company_data = generate_company_overview_data(company, time_stamps)  # Pass start_date and end_date
            report.append(company_data)

        return jsonify(report)

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Failed to generate report'}), 500


def generate_user_report_data(user_email, time_stamps, start_date, end_date):
    # if not time_stamps:
    #     return {}  # Return empty object if no time stamps found

    user: User = User.query.filter_by(email=user_email).first()
    employee_name = user.first_name + " " + user.last_name
    total_hours_worked = 0
    daily_breakdown = []
    salary = float(user.salary or 0)  # Get salary, handle potential None, convert to float
    paid_days_off = 0
    unpaid_days_off = 0
    days_not_reported = 0
    days_worked = 0
    potential_work_days = 0
    current_date = start_date
    while current_date <= end_date:
        found_entry = False
        work_type = None
        daily_hours = 0
        if not user.weekend_choice or current_date.strftime('%A').lower() not in map(str.lower, user.weekend_choice.split(',')):  # potential_work_days += 1
            potential_work_days += 1
            for ts in time_stamps:
                if ts.punch_in_timestamp.date() == current_date.date():
                    found_entry = True
                    if ts.reporting_type == "work":
                        work_type = "work"
                        days_worked += 1
                        daily_hours += ts.total_work_time or 0
                        
                    elif ts.reporting_type == 'paidoff':
                        paid_days_off += 1
                        daily_hours = 8 * 3600
                        work_type = ts.reporting_type
                        break
                    elif ts.reporting_type == 'unpaidoff':
                        unpaid_days_off += 1
                        daily_hours = 0
                        work_type = ts.reporting_type
                        break
                    
                    break
            if not found_entry:
                days_not_reported += 1
            
            total_hours_worked += daily_hours

        daily_breakdown.append({
            "date": current_date.strftime('%Y-%m-%d'),
            "hoursWorked": format_hours_to_hhmm(daily_hours),
            "reportingType": work_type
        })
        current_date += timedelta(days=1)

    total_payment_required = (total_hours_worked / 3600.0) * salary  # Calculate payment (salary is already a float)

    report = {
        "employeeName": employee_name,
        "daysWorked": days_worked,
        "paidDaysOff": paid_days_off,        # Add paidDaysOff to the report
        "unpaidDaysOff": unpaid_days_off,    # Add unpaidDaysOff to the report
        "daysNotReported": days_not_reported,  # Add daysNotReported to the report
        "potentialWorkDays": potential_work_days, 
        "totalHoursWorked": format_hours_to_hhmm(total_hours_worked),
        "workCapacityforRange":format_hours_to_hhmm(calculate_work_capacity(user, start_date, end_date) * 3600),
        "totalPaymentRequired": round(total_payment_required, 2),
        "dailyBreakdown": daily_breakdown,
        "userDetails": {  # Add user details section
            "email": user.email,
            "role": user.role,
            "phone": user.mobile_phone,
            "salary": salary,  # Use the float value directly
            "workCapacity": format_hours_to_hhmm(float(user.work_capacity or 0) * 3600),  # Handle potential None, convert to float
            "weekendChoice": user.weekend_choice
        }
    }

    return report

def generate_company_summary_data(company_id, time_stamps, start_date, end_date):
    # if not time_stamps:
    #     return {}  # Return empty object if no time stamps found

    # Group time stamps by user
    time_stamps_by_user = {}  
    
    users: User = User.query.filter_by(company_id=company_id, is_active=True).all() 
    report = []
    for user in users:
        employee_name = user.first_name + " " + user.last_name
        salary = float(user.salary or 0)

        # Calculate days worked, paid off, unpaid off, and not reported
        days_worked = 0
        paid_days_off = 0
        unpaid_days_off = 0
        days_not_reported = 0
        total_hours_worked =0
        potential_work_days = 0
        current_date = start_date
        while current_date <= end_date:
            isWeekend = False
            daily_hours = 0
            found_entry = False
            # for ts in user_time_stamps:
            for ts in user.timestamps :
                if ts.punch_in_timestamp.date() == current_date.date():
                    if ts.reporting_type == "work":
                        if not found_entry:
                            days_worked += 1
                        found_entry = True
                        daily_hours += ts.total_work_time or 0
                    elif ts.reporting_type == 'paidoff':
                        if not found_entry:
                            paid_days_off += 1
                        found_entry = True
                        daily_hours = 8 * 3600
                        break
                    elif ts.reporting_type == 'unpaidoff':
                        if not found_entry:
                            unpaid_days_off += 1
                        found_entry = True
                        daily_hours = 0
                        break
            if user.weekend_choice and current_date.strftime('%A').lower() in map(str.lower, user.weekend_choice.split(',')):
                isWeekend = True
                
            if not found_entry and not isWeekend: 
                days_not_reported += 1
            
            if not isWeekend:
                potential_work_days += 1
                
            total_hours_worked += daily_hours
            current_date += timedelta(days=1)

        # Calculate total hours worked (only for "work" entries)
        total_payment_required = (total_hours_worked / 3600.0) * salary

        report.append({
            "employeeName": employee_name,
            "userDetails": {
                "email": user.email,
                "role": user.role,
                "phone": user.mobile_phone,
                "salary": salary,
                "workCapacity": format_hours_to_hhmm((user.work_capacity or 0) * 3600)
            },
            "daysWorked": days_worked,
            "paidDaysOff": paid_days_off,
            "unpaidDaysOff": unpaid_days_off,
            "daysNotReported": days_not_reported,
            "potentialWorkDays": potential_work_days, 
            "workCapacityforRange": format_hours_to_hhmm(calculate_work_capacity(user, start_date, end_date) * 3600),
            "totalHoursWorked": format_hours_to_hhmm(total_hours_worked),
            "totalPaymentRequired": round(total_payment_required, 2),
        })

    return report



def generate_company_overview_data(company, time_stamps):
    employees = User.query.filter_by(company_id=company.company_id, is_active=True).all()
    num_employees = len(employees)
    total_hours_worked = 0
    total_monthly_salary = 0
    monthly_payments = []

    for employee in employees:
        employee_time_stamps = [ts for ts in time_stamps if ts.user_email == employee.email]
        employee_hours_worked = 0
        for ts in employee_time_stamps:
            employee_hours_worked += ts.total_work_time or 0
        
        total_hours_worked += employee_hours_worked

        # Calculate monthly payment for the employee
        monthly_payment = (employee_hours_worked / 3600.0) * float(employee.salary or 0)
        total_monthly_salary += monthly_payment
        monthly_payments.append(round(monthly_payment, 2))
    
    admin_users = User.query.filter(
                    User.company_id == company.company_id, 
                    User.permission.in_([E_PERMISSIONS.employer, E_PERMISSIONS.net_admin]),  # Use in_() to check multiple values
                    User.is_active == True ).all()
    admin_names = [admin.first_name + " " + admin.last_name for admin in admin_users]
    return {
        "companyName": company.company_name,
        "numEmployees": num_employees,
        "totalHoursWorked": format_hours_to_hhmm(total_hours_worked),  # Convert to hours
        "totalMonthlySalary": round(total_monthly_salary, 2),
        "monthlyPayments": monthly_payments,
        "adminNames": admin_names
    }