# pylint: disable=import-outside-toplevel
from datetime import datetime, timedelta

from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from djantic import ModelSchema
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from projectx.api.routing import router

JWT_SECRET = settings.JWT_SECRET
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


class JWTToken(BaseModel):  # pylint: disable=too-few-public-methods
    access_token: str
    token_type: str


def schema_for_django_user(fields):

    UserModel = get_user_model()  # pylint: disable=invalid-name

    class DjangoUserSchema(ModelSchema):  # pylint: disable=too-few-public-methods
        class Config:  # pylint: disable=too-few-public-methods
            model = UserModel
            include = fields

        @classmethod
        def from_model(cls, instance: UserModel):
            """
            Convert a Django model instance to an SingleSchema instance.
            """
            return cls(**{field: getattr(instance, field) for field in fields})

    return DjangoUserSchema


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user_func(get_user):
    def inner(token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if not username:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials - empty username",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except JWTError as jwt_error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials - bad token",
                headers={"WWW-Authenticate": "Bearer"},
            ) from jwt_error
        user = get_user(username=username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials - no such user",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    return inner


def get_user_schema():
    return schema_for_django_user(["public_uuid", "email", "first_name", "last_name", "is_active"])


def get_user_authentication():
    def get_user_func(username: str):
        User = get_user_model()  # pylint: disable=invalid-name
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    return get_current_user_func(get_user_func)


class UsersConfig(AppConfig):
    name = "projectx.users"

    def ready(self):
        UserSchema = get_user_schema()
        User = get_user_model()  # pylint: disable=invalid-name
        authentication = get_user_authentication()

        def get_current_active_user(current_user: User = Depends(authentication)):
            if not current_user.is_active:
                raise HTTPException(status_code=400, detail="Inactive user")
            return current_user

        @router.post(
            "/auth/token/",
            summary="Create a new authentication token.",
            tags=["auth"],
            name="auth-token",
            response_model=JWTToken,
        )
        def get_auth_token(form_data: OAuth2PasswordRequestForm = Depends()):
            user = authenticate(None, username=form_data.username, password=form_data.password)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
            return {"access_token": access_token, "token_type": "bearer"}

        @router.get(
            "/auth/self/",
            summary="Get the current authenticated user.",
            tags=["auth"],
            name="auth-self",
            response_model=UserSchema,
        )
        async def auth_self(current_user: User = Depends(get_current_active_user)):
            return UserSchema.from_model(current_user)
