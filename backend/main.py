from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from endpoints.auth import auth_blueprint
from endpoints.companies import companies_blueprint
from endpoints.users import users_blueprint
from endpoints.timestamps import timestamps_bp
from config import Config
from dotenv import load_dotenv
from models import db
from flask_jwt_extended import JWTManager
import sys
import os
from datetime import timedelta

backend_parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the parent directory to Python's search path
if backend_parent_dir not in sys.path:
    sys.path.insert(0, backend_parent_dir)

BASE_API = "/api"
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

# Apply CORS globally before registering blueprints
CORS(app, resources={r"/*": {"origins": f"http://{Config.WEB_URL}:{Config.WEB_PORT}", "supports_credentials": True}})
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}/{Config.DB_NAME}'  # Replace with your actual database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional, but recommended
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)  # 1-hour access token expiration
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30) # 30-day refresh token expiration

db.init_app(app)
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(auth_blueprint, url_prefix=BASE_API+'/auth')
app.register_blueprint(companies_blueprint, url_prefix=BASE_API + '/companies')
app.register_blueprint(users_blueprint, url_prefix=BASE_API + '/users')
app.register_blueprint(timestamps_bp, url_prefix=BASE_API + '/timestamps')

# Error handler for 404 with CORS headers
@app.errorhandler(404)
@cross_origin(origin='http://localhost:5173', supports_credentials=True)
def not_found(error):
    response = jsonify({'error': 'Not found'})
    response.status_code = 404
    return response

# Print all registered routes
if __name__ == '__main__':
    print("Registered Routes:")
    for rule in app.url_map.iter_rules():
        print(rule)
    
    app.run(debug=True, port=3000)
