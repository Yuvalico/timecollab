from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from endpoints.auth import auth_blueprint
from endpoints.companies import companies_blueprint 
from endpoints.users import users_blueprint
from config import Config
from dotenv import load_dotenv
from models import db
import sys
import os

backend_parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the parent directory to Python's search path
if backend_parent_dir not in sys.path:
    sys.path.insert(0, backend_parent_dir)

BASE_API = "/api"
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS and allow credentials
CORS(app, resources={r"/*": {"origins": "http://localhost:5173", "supports_credentials": True}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:kokonoko@127.0.0.1/tlv300'  # Replace with your actual database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional, but recommended

db.init_app(app)  

# Register the blueprints
app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(companies_blueprint, url_prefix=BASE_API+'/companies')
app.register_blueprint(users_blueprint, url_prefix=BASE_API+'/users')

if __name__ == '__main__':
    app.run(debug=True, port=3000)
