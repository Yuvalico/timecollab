from flask_jwt_extended import create_access_token, create_refresh_token
from models import User
from classes.RC import RC, E_RC
from classes.UserRepository import UserRepository
from classes.ModelValidator import ModelValidator
from classes.BaseServiceClass import BaseService
from classes.DomainClassFactory import DomainClassFactory
from cmn_utils import *
import bcrypt


class AuthService(BaseService):
    def __init__(self, user_repository: UserRepository, validator: ModelValidator, factory: DomainClassFactory):
        super().__init__(validator, factory)
        self.user_repository = user_repository
        self.validator = validator

    def login(self, email: str, password: str) -> tuple[str, str] | RC:
        try:
            user: User | RC = self.user_repository.get_user_by_email(email)
            if isinstance(user, RC):
                return user

            if not user.pass_hash:
                return RC(E_RC.RC_INVALID_INPUT, 'Password not set for this user')

            if not bcrypt.checkpw(password.encode('utf-8'), user.pass_hash.encode('utf-8')):
                return RC(E_RC.RC_INVALID_INPUT, 'Invalid credentials')

            additional_claims = {
                'permission': user.permission,
                'company_id': user.company_id
            }
            access_token = create_access_token(
                identity=user.email,
                fresh=True,
                additional_claims=additional_claims)
            refresh_token = create_refresh_token(identity=user.email)

            return {"access_token" :access_token, 
                    "refresh_token": refresh_token,
                    "permission": user.permission,
                    "company_id": user.company_id
                    }

        except Exception as e:
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, 'Server error')

    def refresh(self, current_user: str) -> tuple[str, str] | RC:
        try:
            # Query the user
            user: User | RC = self.user_repository.get_user_by_email(email=current_user)
            if isinstance(user, RC):
                return user

            additional_claims = {
                'permission': user.permission,
                'company_id': user.company_id
            }
            new_access_token = create_access_token(
                identity=current_user,
                fresh=False,
                additional_claims=additional_claims)
            
            new_refresh_token = create_refresh_token(identity=current_user)

            return {"new_access_token": new_access_token,
                    "new_refresh_token": new_refresh_token
                    }   

        except Exception as e:
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, 'Server error')