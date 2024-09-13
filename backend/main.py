from flask import Flask
from flask_cors import CORS
from endpoints.auth import auth_blueprint
from endpoints.companies import companies_blueprint 
from endpoints.users import users_blueprint
from config import Config
from dotenv import load_dotenv

BASE_API = "/api"
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS and allow credentials
CORS(app, resources={r"/*": {"origins": "http://localhost:5173", "supports_credentials": True}})

# Register the blueprints
app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(companies_blueprint, url_prefix=BASE_API+'/companies')
app.register_blueprint(users_blueprint, url_prefix=BASE_API+'/users')

if __name__ == '__main__':
    app.run(debug=True, port=3000)
