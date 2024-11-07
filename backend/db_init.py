from models import CompanyModel, UserModel
from tabulate import tabulate
import datetime
import re
from datetime import datetime, timezone, timedelta
import psycopg2
from flask_jwt_extended import get_jwt_identity, get_jwt
from sqlalchemy import create_engine, text  
from sqlalchemy_utils import database_exists, create_database
from config import *
import bcrypt
from classes.Permission import E_PERMISSIONS



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
        if not CompanyModel.query.filter_by(company_name="NetAdmin Company").first():
            print("Creating NetAdmin company...")
            company = CompanyModel(company_name="NetAdmin Company")
            db.session.add(company)
            db.session.commit()
            print("NetAdmin company created successfully.")
        else:
            print("NetAdmin company already exists.")

        # Check if a net admin user already exists
        if not UserModel.query.filter_by(email='a@gmail.com').first():
            print("Creating net admin user...")

            # Get the NetAdmin company (it should exist now)
            company: CompanyModel = CompanyModel.query.filter_by(company_name="NetAdmin Company").first()

            # Create the net admin user
            net_admin = UserModel(
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
            company = CompanyModel.query.filter_by(company_name=company_name).first()
            if not company:
                company = CompanyModel(company_name=company_name)
                db.session.add(company)
                companies.append(company)
                print(f"{company_name} created successfully.")
        db.session.commit()

        # Create users for each company
        for company in companies:
            # Create employer user
            employer: UserModel = UserModel.query.filter_by(email=f'{company.company_name}_employer@example.com').first()
            if not employer:
                employer = UserModel(
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
            employee: UserModel = UserModel.query.filter_by(email=f'{company.company_name}_employee@example.com').first()
            if not employee:
                employee = UserModel(
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