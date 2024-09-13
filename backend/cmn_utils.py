import traceback
from tabulate import tabulate
import datetime
import re
import psycopg2


def print_exception(exception):
    """Prints a formatted exception message in a table with a vertical separator.

    Args:
        exception: The exception object.
    """

    tb = traceback.extract_tb(exception.__traceback__)[-1]
    exception_type = type(exception).__name__
    exception_message = str(exception)
    timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
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