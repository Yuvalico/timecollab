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
from cmn_defs import *

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