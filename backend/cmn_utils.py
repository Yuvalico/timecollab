import traceback
from tabulate import tabulate
import datetime
import re
from datetime import datetime, timezone, timedelta
import psycopg2
from flask_jwt_extended import get_jwt_identity, get_jwt
from sqlalchemy import create_engine, text  
from sqlalchemy_utils import database_exists, create_database
from config import *
from models import *
from cmn_defs import *
import bcrypt

def print_exception(exception):
    """Prints a formatted exception message in a table with a vertical separator.

    Args:
        exception: The exception object.
    """

    tb = traceback.extract_tb(exception.__traceback__)[-1]
    exception_type = type(exception).__name__
    exception_message = str(exception)
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    path_idx = find_timewatch_re(tb.filename)
    if -1 != path_idx:
        tb.filename = tb.filename[path_idx:]

    table_data = [
        [timestamp, "|", exception_type, "|", exception_message, "|", tb.filename, "|", tb.lineno]
    ]

    print(tabulate(table_data, tablefmt="simple", numalign="left", stralign="left"))

def find_timewatch_re(string):
    match = re.search(r"timeWatch", string)
    if not match:
        match = re.search(r"tw", string)

    return match.start() if match else -1

def get_db_connection(config: dict):
    conn = psycopg2.connect(
        host=config['DB_HOST'],
        database=config['DB_NAME'],
        user=config['DB_USER'],
        password=config['DB_PASSWORD']
    )
    return conn

def extract_jwt():
    current_user_email = get_jwt_identity()
    claims = get_jwt()
    user_permission = claims.get('permission') 
    user_company_id = claims.get('company_id') 
    
    return current_user_email, user_permission, user_company_id

def create_db(app, db):
    """Creates the database if it does not exist."""
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if not database_exists(db_uri):
        print(f"Database '{Config.DB_NAME}' not found. Creating...")
        create_database(db_uri)  # Create the database using sqlalchemy_utils
        print(f"Database '{Config.DB_NAME}' created successfully.")

    with app.app_context():
        # Connect to the database
        engine = db.get_engine()

        # Enable uuid-ossp extension
        with engine.connect() as conn:
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
            conn.commit()  # Ensure the command is committed

        # Create all tables
        db.create_all()  # No need to pass 'bind' anymore
        print("Tables created successfully.")

        # Check if NetAdmin company already exists
        if not Company.query.filter_by(company_name="NetAdmin Company").first():
            print("Creating NetAdmin company...")
            company = Company(company_name="NetAdmin Company")
            db.session.add(company)
            db.session.commit()
            print("NetAdmin company created successfully.")
        else:
            print("NetAdmin company already exists.")

        # Check if a net admin user already exists
        if not User.query.filter_by(email='a@gmail.com').first():
            print("Creating net admin user...")

            # Get the NetAdmin company (it should exist now)
            company: Company = Company.query.filter_by(company_name="NetAdmin Company").first()

            # Create the net admin user
            net_admin = User(
                email='a@gmail.com',
                first_name='Net',
                last_name='Admin',
                company_id=company.company_id,  # Assign to NetAdmin company
                role='Net Admin',
                permission=E_PERMISSIONS.net_admin,  # Assuming 5 is the permission level for net admin
                pass_hash=bcrypt.hashpw('123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                is_active=True
            )
            db.session.add(net_admin)
            db.session.commit()
            print("Net admin user created successfully.")
        else:
            print("Net admin user already exists.")

        ############ create test data #####################
        company_names = ['tlv300', 'test1']
        companies = []
        for company_name in company_names:
            company = Company.query.filter_by(company_name=company_name).first()
            if not company:
                company = Company(company_name=company_name)
                db.session.add(company)
                companies.append(company)
                print(f"{company_name} created successfully.")
        db.session.commit()

        # Create users for each company
        for company in companies:
            # Create employer user
            employer: User = User.query.filter_by(email=f'{company.company_name}_employer@example.com').first()
            if not employer:
                employer = User(
                    email=f'employer@{company.company_name}.com',
                    first_name='Employer',
                    last_name=company.company_name,
                    company_id=company.company_id,
                    role='Manager',
                    permission=E_PERMISSIONS.employer,  # Assuming 4 is the permission level for employer
                    pass_hash=bcrypt.hashpw('123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    is_active=True
                )
                db.session.add(employer) 
                print(f"{company.company_name} employer created successfully.")

            # Create employee user
            employee: User = User.query.filter_by(email=f'{company.company_name}_employee@example.com').first()
            if not employee:
                employee = User(
                    email=f'employee@{company.company_name}.com',
                    first_name='Employee',
                    last_name=company.company_name,
                    company_id=company.company_id,
                    role='secretary',
                    permission=E_PERMISSIONS.employee,  # Assuming 1 is the permission level for employee
                    pass_hash=bcrypt.hashpw('123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    is_active=True 
                )
                db.session.add(employee)
                print(f"{company.company_name} employee created successfully.")
            db.session.commit()

        engine.dispose()
        
def calculate_work_capacity(user, start_date, end_date):
    # Calculate the number of potential work days in the date range (excluding weekends)
    num_work_days = 0
    current_date = start_date
    while current_date <= end_date:
        if not user.weekend_choice or current_date.strftime('%A').lower() not in map(str.lower, user.weekend_choice.split(',')):
            num_work_days += 1
        current_date += timedelta(days=1)

    # Calculate total work capacity for the date range
    daily_work_capacity = float(user.work_capacity or 0)
    total_work_capacity = daily_work_capacity * num_work_days

    return round(total_work_capacity, 2)

def format_hours_to_hhmm(seconds):
  """
  Formats a duration in seconds to the HH:MM format.

  Args:
    seconds: The duration in seconds.

  Returns:
    A string representing the duration in HH:MM format.
  """
  hours = int(seconds // 3600)
  minutes = int((seconds % 3600) // 60)
  return f"{hours:02d}:{minutes:02d}"