import psycopg2

def initialize_database(config):
  """Initializes the PostgreSQL database with the provided schema.

  Args:
      config: A dictionary containing the database connection configuration
              (host, database, user, password).
  """

  conn = psycopg2.connect(**config)
  cursor = conn.cursor()

  try:
      # Create the 'uuid-ossp' extension if it doesn't exist
      cursor.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")

      # Create the 'users' table if it doesn't exist
      cursor.execute("""
          CREATE TABLE IF NOT EXISTS users (
              id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
              first_name VARCHAR(255),
              last_name VARCHAR(255),
              mobile_phone VARCHAR(20),
              email VARCHAR(255),
              company_id UUID,
              role VARCHAR(255),
              permission INTEGER,
              pass_hash VARCHAR(255),
              is_active BOOLEAN,
              salary NUMERIC,
              work_capacity NUMERIC
          );
      """)

      # Create the index on the 'id' column if it doesn't exist
      cursor.execute("CREATE INDEX IF NOT EXISTS users_new_pkey ON users USING btree (id);")

      # Create the 'companies' table if it doesn't exist
      cursor.execute("""
          CREATE TABLE IF NOT EXISTS companies (
              company_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
              company_name VARCHAR(255) NOT NULL,
              is_active BOOLEAN DEFAULT true
          );
      """)

      # Create the index on the 'company_id' column if it doesn't exist
      cursor.execute("CREATE INDEX IF NOT EXISTS companies_pkey ON companies USING btree (company_id);")

      conn.commit()  # Commit the changes to the database
      print("Database initialized successfully!")

  except (Exception, psycopg2.Error) as error:
      print("Error initializing database:", error)
  finally:
      if conn:
          cursor.close()
          conn.close()

# Example usage (replace with your actual configuration)
config = {
  'host': 'localhost',
  'database': 'tlv300',
  'user': 'postgres',
  'password': 'kokonoko'
}

initialize_database(config)