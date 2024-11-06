from flask import Blueprint, request, jsonify
from models import db, User, TimeStamp, Company
from datetime import datetime, timezone, timedelta
from cmn_utils import *
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from cmn_defs import *
import calendar
from classes.Company import Company
from classes.User import User
from classes.TimeStamp import TimeStamp
from classes.CompanyRepository import CompanyRepository
from classes.UserRepository import UserRepository
from classes.TimeStampRepository import TimeStampRepository
from classes.ReportService import ReportService

reports_bp = Blueprint('reports', __name__)

company_repository = CompanyRepository(db)
user_repository = UserRepository(db)
timestamp_repository = TimeStampRepository(db)
report_service = ReportService(user_repository, timestamp_repository, company_repository)

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

        requested_user: User = user_repository.get_user_by_email(current_user_email)
        if isinstance (requested_user,RC):
            return createRcjson(requested_user)
        
        # Permission check for accessing other user's reports
        if user_email and user_email != current_user_email \
                and user_permission == E_PERMISSIONS.employee:
            return jsonify({'error': 'Unauthorized to access this report'}), E_RC.RC_UNAUTHORIZED

        if E_PERMISSIONS.employer == user_permission and (
                user_company_id != company_id
                or str(requested_user.company_id) != str(user_company_id)):
            return jsonify({'error': 'Unauthorized to access this report'}), E_RC.RC_UNAUTHORIZED
        
        # Determine date range
        if date_range_type == 'monthly':
            if not selected_year or not selected_month:
                return jsonify({'error': 'Year and month are required for monthly reports'}), E_RC.RC_INVALID_INPUT

            year = int(selected_year)
            month = int(selected_month)
            start_date = datetime(year, month, 1, tzinfo=timezone.utc)
            end_date = datetime(year, month, calendar.monthrange(year, month)[1], tzinfo=timezone.utc)
        elif date_range_type == 'custom':
            if not start_date_str or not end_date_str:
                return jsonify({'error':'Start and end dates are required for custom reports'}), E_RC.RC_INVALID_INPUT
            try:
                start_date = iso2datetime(start_date_str),
                end_date = iso2datetime(end_date_str),
                if end_date < start_date:
                    return jsonify({'error': 'Start date must earlier than end date'}), E_RC.RC_INVALID_INPUT
                
            except ValueError:
                return jsonify({'error': 'Invalid date format'}), E_RC.RC_INVALID_INPUT
        else:
            return jsonify({'error': 'Invalid date range type'}), E_RC.RC_INVALID_INPUT

        time_stamps = timestamp_repository.get_range(start_date, end_date, user_email)

        report = report_service.user_report(user_email, time_stamps, start_date, end_date)
        return jsonify(report)

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Failed to generate report'}), E_RC.RC_ERROR_DATABASE

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

        if not company_id:
            return jsonify({'error': 'Company ID is required'}), E_RC.RC_INVALID_INPUT

        company: Company | RC = company_repository.get_company_by_id(company_id)
        if isinstance(company, RC):
            return createRcjson(company)

        if user_permission == E_PERMISSIONS.employee:
            return jsonify({'error': 'Unauthorized to access this report'}), E_RC.RC_UNAUTHORIZED

        if E_PERMISSIONS.employer == user_permission and str(user_company_id) != str(company_id):
            return jsonify({'error': 'Unauthorized to access this report'}), E_RC.RC_UNAUTHORIZED

        if date_range_type == 'monthly':
            if not selected_year or not selected_month:
                return jsonify({'error': 'Year and month are required for monthly reports'}), E_RC.RC_INVALID_INPUT

            year = int(selected_year)
            month = int(selected_month)
            start_date = datetime(year, month, 1, tzinfo=timezone.utc)
            end_date = datetime(year, month, calendar.monthrange(year, month)[1], tzinfo=timezone.utc)
            
        elif date_range_type == 'custom':
            if not start_date_str or not end_date_str:
                return jsonify({'error': 'Start and end dates are required for custom reports'}), E_RC.RC_INVALID_INPUT
            try:
                start_date = iso2datetime(start_date_str)
                end_date = iso2datetime(end_date_str)
            except ValueError:
                return jsonify({'error': 'Invalid date format'}), E_RC.RC_INVALID_INPUT
        else:
            return jsonify({'error': 'Invalid date range type'}), E_RC.RC_INVALID_INPUT

        time_stamps = timestamp_repository.get_range(start_date, end_date, company_id=company_id)

        report = report_service.company_summary(company_id, time_stamps, start_date, end_date)
        return jsonify(report), E_RC.RC_OK

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Failed to generate report'}), E_RC.RC_ERROR_DATABASE

@reports_bp.route('/generate-company-overview', methods=['GET'])
@jwt_required()
def generate_company_overview_report():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        # Permission check (only for netadmins)
        if user_permission != E_PERMISSIONS.net_admin:
            return jsonify({'error': 'Unauthorized to access this report'}), E_RC.RC_UNAUTHORIZED

        date_range_type = request.args.get('dateRangeType')
        selected_year = request.args.get('year')
        selected_month = request.args.get('month')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        # Determine date range
        if date_range_type == 'monthly':
            if not selected_year or not selected_month:
                return jsonify({'error': 'Year and month are required for monthly reports'}), E_RC.RC_INVALID_INPUT

            year = int(selected_year)
            month = int(selected_month)
            start_date = datetime(year, month, 1, tzinfo=timezone.utc)
            end_date = datetime(year, month, calendar.monthrange(year, month)[1], tzinfo=timezone.utc)

        elif date_range_type == 'custom':
            if not start_date_str or not end_date_str:
                return jsonify({'error': 'Start and end dates are required for custom reports'}), E_RC.RC_INVALID_INPUT
            try:
                start_date = iso2datetime(start_date_str),
                end_date = iso2datetime(end_date_str),
            except ValueError:
                return jsonify({'error': 'Invalid date format'}), E_RC.RC_INVALID_INPUT
        else:
            return jsonify({'error': 'Invalid date range type'}), E_RC.RC_INVALID_INPUT

        companies: list[Company] = company_repository.get_all_active_companies()  # Add is_active filter

        report = []
        for company in companies:
            time_stamps = timestamp_repository.get_range(start_date, end_date, company.company_id)

            company_data = report_service.company_overview(company, time_stamps)
            report.append(company_data)

        return jsonify(report), E_RC.RC_OK

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Failed to generate report'}), E_RC.RC_ERROR_DATABASE

