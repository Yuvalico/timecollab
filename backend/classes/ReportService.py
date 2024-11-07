from classes.Company import Company
from classes.User import User
from classes.TimeStamp import TimeStamp
from classes.CompanyRepository import CompanyRepository
from classes.UserRepository import UserRepository
from classes.TimeStampRepository import TimeStampRepository
from classes.Permission import Permission
from classes.BaseServiceClass import BaseService
from classes.ModelValidator import ModelValidator
from classes.DomainClassFactory import DomainClassFactory
from classes.RC import RC, E_RC
from cmn_utils import *
from datetime import datetime, timezone, timedelta
import calendar


class ReportService(BaseService):
    def __init__(self, user_repository: UserRepository, timestamp_repository: TimeStampRepository, company_repository: CompanyRepository, validator: ModelValidator, factory: DomainClassFactory):
        super().__init__(validator, factory)
        self.user_repository: UserRepository = user_repository
        self.timestamp_repository: TimeStampRepository = timestamp_repository
        self.company_repository: CompanyRepository = company_repository

    def user_report(self, user_email, date_range_type, selected_year, selected_month, start_date_str, \
            end_date_str, user_permission: int, user_company_id: str, current_user_email: str) -> dict | RC:
        
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if perm.is_employee() and user_email and user_email != current_user_email:
             return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
         
        result = self._set_dates_range(date_range_type, selected_year, selected_month, start_date_str, end_date_str)
        if isinstance(result, RC):
            return result
        
        start_date, end_date = result

        user: User = self.user_repository.get_user_by_email(user_email)
        if isinstance (user, RC):
            return user
        
        if perm.is_employer() and (str(user.company_id) != str(user_company_id)):
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
        
        time_stamps = self.timestamp_repository.get_range(start_date, end_date, user_email)
        if isinstance(time_stamps, RC):
            return time_stamps

        days_worked, paid_days_off, unpaid_days_off, days_not_reported, total_hours_worked,\
            potential_work_days, daily_breakdown = self._calculate_work_days(user, time_stamps, start_date, end_date)

        report_entry: dict = self._generate_report_entry(user, days_worked, paid_days_off, unpaid_days_off, days_not_reported, total_hours_worked, potential_work_days, start_date, end_date, daily_breakdown)

        return report_entry

    def company_summary(self, company_id: str, date_range_type: str, selected_year: str, selected_month: str, start_date_str: str, \
                end_date_str: str, user_permission: int, user_company_id: str) -> dict|RC:
        
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if perm.is_employee():
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
        
        if perm.is_employer() and (str(user_company_id) != str(company_id)):
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
        
        result = self._set_dates_range(date_range_type, selected_year, selected_month, start_date_str, end_date_str)
        if isinstance(result, RC):
            return result
        
        start_date, end_date = result
        
        users: list[User] = self.company_repository.get_company_users(company_id=company_id)
        report = []
        for user in users:
            timestamps: list[TimeStamp] = self.timestamp_repository.get_range(start_date, end_date, user.email)

            days_worked, paid_days_off, unpaid_days_off, days_not_reported, total_hours_worked, potential_work_days, _\
                =self._calculate_work_days(user, timestamps, start_date, end_date)
            
            report_entry: dict = self._generate_report_entry(user, days_worked, paid_days_off, unpaid_days_off, days_not_reported, total_hours_worked, potential_work_days, start_date, end_date)
            report.append(report_entry)

        return report

    def company_overview(self, date_range_type: str, selected_year: str, selected_month: str, start_date_str: str, end_date_str: str, user_permission: int) -> dict| RC:
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if not perm.is_net_admin():
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
        
        result = self._set_dates_range(date_range_type, selected_year, selected_month, start_date_str, end_date_str)
        if isinstance(result, RC):
            return result
        
        start_date, end_date = result
        
        companies: list[Company] = self.company_repository.get_all_active_companies()
        
        report = []
        for company in companies:
            employees: list[User] = self.company_repository.get_company_users(company_id=company.company_id)
            num_employees = len(employees)
            total_hours_worked = 0
            total_monthly_salary = 0
            monthly_payments = []

            for employee in employees:
                employee_time_stamps = self.timestamp_repository.get_range(start_date, end_date, employee.email)
                employee_hours_worked = 0
                for ts in employee_time_stamps:
                    employee_hours_worked += ts.total_work_time or 0
                
                total_hours_worked += employee_hours_worked

                # Calculate monthly payment for the employee
                monthly_payment = (employee_hours_worked / 3600.0) * float(employee.salary or 0)
                total_monthly_salary += monthly_payment
                monthly_payments.append(round(monthly_payment, 2))
            
            admin_users: list[User] = self.company_repository.get_company_admins(company.company_id)
            admin_names = [admin.first_name + " " + admin.last_name for admin in admin_users]
            report.append( {
                "companyName": company.company_name,
                "numEmployees": num_employees,
                "totalHoursWorked": format_hours_to_hhmm(total_hours_worked),
                "totalMonthlySalary": round(total_monthly_salary, 2),
                "monthlyPayments": monthly_payments,
                "adminNames": admin_names
            })
            
        return report
        
        
    def _calculate_work_days(self, user: User, time_stamps: list[TimeStamp], start_date: datetime, end_date: datetime) -> tuple:
        
        total_hours_worked = 0
        daily_breakdown = []
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

        return days_worked, paid_days_off, unpaid_days_off, days_not_reported, total_hours_worked, potential_work_days, daily_breakdown
    
    def _generate_report_entry(self, user: User, days_worked, paid_days_off, unpaid_days_off, days_not_reported, total_hours_worked, potential_work_days, start_date, end_date, daily_breakdown = None):
        employee_name = user.first_name + " " + user.last_name
        salary = float(user.salary or 0)
        total_payment_required = (total_hours_worked / 3600.0) * salary
        
        report = {
            "employeeName": employee_name,
            "daysWorked": days_worked,
            "paidDaysOff": paid_days_off,        
            "unpaidDaysOff": unpaid_days_off,    
            "daysNotReported": days_not_reported,  
            "potentialWorkDays": potential_work_days, 
            "totalHoursWorked": format_hours_to_hhmm(total_hours_worked),
            "workCapacityforRange":format_hours_to_hhmm(calculate_work_capacity(user, start_date, end_date) * 3600),
            "totalPaymentRequired": round(total_payment_required, 2),
            "dailyBreakdown": daily_breakdown,
            "userDetails": {  
                "email": user.email,
                "role": user.role,
                "phone": user.mobile_phone,
                "salary": salary,
                "workCapacity": format_hours_to_hhmm(float(user.work_capacity or 0) * 3600), 
                "weekendChoice": user.weekend_choice
            }
        }
        
        return report
    
    def _set_dates_range(self, date_range_type: str, selected_year: str, selected_month: str, start_date_str: str, end_date_str: str):
        if date_range_type == 'monthly':
            if not selected_year or not selected_month:
                return RC(E_RC.RC_INVALID_INPUT, 'Year and month are required for monthly reports')

            year = int(selected_year)
            month = int(selected_month)
            start_date = datetime(year, month, 1, tzinfo=timezone.utc)
            end_date = datetime(year, month, calendar.monthrange(year, month)[1], tzinfo=timezone.utc)
            return start_date, end_date
        
        elif date_range_type == 'custom':
            if not start_date_str or not end_date_str:
                return RC(E_RC.RC_INVALID_INPUT, 'Start and end dates are required for custom reports')
            try:
                start_date = iso2datetime(start_date_str)
                end_date = iso2datetime(end_date_str)
                if end_date < start_date:
                    return RC(E_RC.RC_INVALID_INPUT, 'Start date must earlier than end date')
                
                return start_date, end_date
            
            except ValueError:
                return RC(E_RC.RC_INVALID_INPUT, 'Invalid date format')
        else:
            return RC(E_RC.RC_INVALID_INPUT, 'Invalid date range type')