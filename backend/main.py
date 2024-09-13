from flask import Flask
from endpoints.auth import auth_blueprint
from endpoints.companies import companies_blueprint 
from endpoints.users import users_blueprint
from config import Config
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config.from_object(Config)
# app.config['SECRET_KEY'] = 'your_jwt_secret_key'  # Replace this with a real secret key

# Register the blueprints
app.register_blueprint(auth_blueprint)
app.register_blueprint(companies_blueprint, url_prefix='/companies')
app.register_blueprint(users_blueprint, url_prefix='/users')

if __name__ == '__main__':
    app.run(debug=True)