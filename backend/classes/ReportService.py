from classes.Company import Company
from classes.User import User
from classes.TimeStamp import TimeStamp
from classes.CompanyRepository import CompanyRepository
from classes.UserRepository import UserRepository
from classes.TimeStampRepository import TimeStampRepository
from cmn_defs import *
from cmn_utils import *
from datetime import datetime, timezone, timedelta


class ReportService:
    def __init__(self, user_repository: UserRepository, timestamp_repository: TimeStampRepository, company_repository: CompanyRepository):
        self.user_repository: UserRepository = user_repository
        self.timestamp_repository: TimeStampRepository = timestamp_repository
        self.company_repository: CompanyRepository = company_repository

    def user_report(self, user_email: str, time_stamps: list[TimeStamp], start_date: datetime, end_date: datetime) -> dict | RC:

        user: User = self.user_repository.get_user_by_email(user_email)
        if isinstance (user,RC):
            return user
        
        employee_name = user.first_name + " " + user.last_name
        salary = float(user.salary or 0)  # Get salary, handle potential None, convert to float

        days_worked, paid_days_off, unpaid_days_off, days_not_reported, total_hours_worked,\
            potential_work_days, daily_breakdown = self._calculate_work_days(user, time_stamps, start_date, end_date)

        report_entry: dict = self._generate_report_entry(user, days_worked, paid_days_off, unpaid_days_off, days_not_reported, total_hours_worked, potential_work_days, start_date, end_date, daily_breakdown)

        return report_entry

    def company_summary(self, company_id, time_stamps, start_date, end_date):

        users: list[User] = self.company_repository.get_company_users(company_id=company_id)
        report = []
        for user in users:
            timestamps: list[TimeStamp] = self.timestamp_repository.get_range(start_date, end_date, user.email)

            # Calculate days worked, paid off, unpaid off, and not reported
            days_worked = 0
            paid_days_off = 0
            unpaid_days_off = 0
            days_not_reported = 0
            total_hours_worked =0
            potential_work_days = 0
            
            days_worked, paid_days_off, unpaid_days_off, days_not_reported, total_hours_worked, potential_work_days, _\
                =self._calculate_work_days(user, timestamps, start_date, end_date)
            
            report_entry: dict = self._generate_report_entry(user, days_worked, paid_days_off, unpaid_days_off, days_not_reported, total_hours_worked, potential_work_days, start_date, end_date)
            report.append(report_entry)

        return report

    def company_overview(self, company: Company, time_stamps: list[TimeStamp]):
        employees: list[User] = self.company_repository.get_company_users(company_id=company.company_id)
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
        
        admin_users: list[User] = self.company_repository.get_company_admins(company.company_id)
        admin_names = [admin.first_name + " " + admin.last_name for admin in admin_users]
        return {
            "companyName": company.company_name,
            "numEmployees": num_employees,
            "totalHoursWorked": format_hours_to_hhmm(total_hours_worked),  # Convert to hours
            "totalMonthlySalary": round(total_monthly_salary, 2),
            "monthlyPayments": monthly_payments,
            "adminNames": admin_names
        }
        
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