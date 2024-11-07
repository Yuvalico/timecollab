from flask import Blueprint, request, jsonify
from models import db, User, TimeStamp, Company
from datetime import datetime, timezone, timedelta
from cmn_utils import *
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from classes.CompanyRepository import CompanyRepository
from classes.RC import RC, E_RC
from classes.ModelValidator import ModelValidator
from classes.UserRepository import UserRepository
from classes.TimeStampRepository import TimeStampRepository
from classes.DomainClassFactory import DomainClassFactory
from classes.ReportService import ReportService

reports_bp = Blueprint('reports', __name__)

report_service = ReportService(UserRepository(db), TimeStampRepository(db), CompanyRepository(db), ModelValidator(), DomainClassFactory())

@reports_bp.route('/generate-user', methods=['GET'])
@jwt_required()
def generate_user_report():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()
        claims = get_jwt()

        user_email = request.args.get('user_email')
        date_range_type = request.args.get('dateRangeType')
        selected_year = request.args.get('year')
        selected_month = request.args.get('month')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        report = report_service.user_report(user_email, date_range_type, selected_year, selected_month, start_date_str, end_date_str, user_permission, user_company_id, current_user_email)
        if isinstance(report, RC):
            return report.to_json()
        
        return jsonify(report), E_RC.RC_OK

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

        report = report_service.company_summary(company_id, date_range_type, selected_year, selected_month, start_date_str, end_date_str, user_permission, user_company_id)
        if isinstance(report, RC):
            return report.to_json()
        
        return jsonify(report), E_RC.RC_OK

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Failed to generate report'}), E_RC.RC_ERROR_DATABASE

@reports_bp.route('/generate-company-overview', methods=['GET'])
@jwt_required()
def generate_company_overview_report():
    try:
        current_user_email, user_permission, user_company_id = extract_jwt()

        date_range_type = request.args.get('dateRangeType')
        selected_year = request.args.get('year')
        selected_month = request.args.get('month')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        report = report_service.company_overview(date_range_type, selected_year, selected_month, start_date_str, end_date_str, user_permission)
        if isinstance(report, RC):
            return report.to_json()

        return jsonify(report), E_RC.RC_OK

    except Exception as e:
        print_exception(e)
        return jsonify({'error': 'Failed to generate report'}), E_RC.RC_ERROR_DATABASE

