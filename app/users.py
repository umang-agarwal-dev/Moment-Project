import uuid
from fastapi import Depends,Request
from typing import Optional
from fastapi_users import BaseUserManager,FastAPIUsers,UUIDIDMixin,models
from fastapi_users.authentication import(
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy
)

from fastapi_users.db import SQLAlchemyUserDatabase
from app.db import User , get_user_db
import os

SECRET = os.getenv("SECRET")

class UserManager(UUIDIDMixin,BaseUserManager[User,uuid.UUID]):
    reset_password_token_secret=SECRET
    verification_token_secret=SECRET

    async def on_after_register(self, user, request = None):
        return await super().on_after_register(user, request)
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(self, user, token, request = None):
        return await super().on_after_forgot_password(user, token, request)
        print(f"User {user.id} has forgot their password.Reset Token: {token}")

        
    async def on_after_request_verify(self, user, token, request = None):
        return await super().on_after_request_verify(user, token, request)
        print(f"verification requested for user {user.id}. Verification Token: {token}")

async def get_user_manager(user_db:SQLAlchemyUserDatabase=Depends(get_user_db)):
    yield UserManager(user_db)

bearer_Transport=BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy():
    return JWTStrategy(secret=SECRET,lifetime_seconds=3600)

auth_backend=AuthenticationBackend(
    name="jwt",
    transport=bearer_Transport,
    get_strategy=get_jwt_strategy,
)
fastapi_users=FastAPIUsers[User,uuid.UUID](
    get_user_manager,auth_backends=[auth_backend])
current_active_user=fastapi_users.current_user(active=True)