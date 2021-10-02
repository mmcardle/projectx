import calendar
import json
import logging
import secrets
import uuid

from asgiref.sync import AsyncToSync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core import signing
from django.core.mail import send_mail
from django.core.signing import BadSignature
from django.db import models
from django_redis import get_redis_connection

from projectx.common.models import IndexedTimeStampedModel
from projectx.users import emails
from projectx.users.fields import LowercaseEmailField

logger = logging.getLogger(__name__)

REDIS_PASSWORD_RESET_KEY = "password_reset"
PASSWORD_RESET_SALT = "password_reset"

REDIS_ACCOUNT_ACTIVATION_KEY = "account_activation"
ACCOUNT_ACTIVATION_SALT = "account_activation"

MAX_PASSWORD_RESET_HOURS = 24
MAX_PASSWORD_RESET_SECONDS = 60 * 60 * MAX_PASSWORD_RESET_HOURS

MAX_ACTIVATION_HOURS = 24
MAX_ACTIVATION_SECONDS = 60 * 60 * MAX_ACTIVATION_HOURS


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        email = self.normalize_email(email)
        if "username" not in kwargs:
            kwargs["username"] = email
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, **kwargs):
        user = self.create_user(**kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractUser, IndexedTimeStampedModel):

    email = LowercaseEmailField(max_length=255, unique=True)
    public_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def display_name(self):
        return self.get_full_name()

    def __str__(self):
        return self.display_name()

    @property
    def public_id(self):
        return str(self.public_uuid)

    def role(self):
        return "admin" if self.is_staff else "user"

    def unique_name(self):
        email_safe = self.email.replace("@", "_").replace(".", "_")
        return f"{email_safe}_{self.public_id[0:8]}"

    def to_json(self):
        data = {
            "role": self.role(),
            "public_id": self.public_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "display_name": self.display_name(),
            "email": self.email,
            "last_login_timestamp": self.last_login_timestamp(),
            "last_login_timestamp_iso": self.last_login_timestamp_iso(),
        }

        return data

    def last_login_timestamp(self):
        if self.last_login:
            return calendar.timegm(self.last_login.utctimetuple())
        return None

    def last_login_timestamp_iso(self):
        if self.last_login:
            return self.last_login.isoformat()
        return None

    def activate(self):
        self.is_active = True
        self.save()

    def send_reset_password_email(self, request):

        key = signing.dumps({"email": self.email}, salt=PASSWORD_RESET_SALT)

        redis_connection = get_redis_connection()
        payload = json.dumps({"key": key}).encode("utf-8")
        redis_connection.hset(REDIS_PASSWORD_RESET_KEY, self.email, payload)

        url = request.build_absolute_uri(f"/password_reset/{key}")

        message = emails.RESET_PASSWORD.format(
            title="ProjectX Password Reset", expiration=f"{MAX_PASSWORD_RESET_HOURS} hours", url=url
        )

        subject = f"Password Reset for {self.email}"

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email])

    def send_data_to_user(self, data):
        payload = json.dumps(data)
        AsyncToSync(get_channel_layer().group_send)(self.unique_name(), {"type": "user.message", "data": payload})

    @classmethod
    def delete_reset_key(cls, key):
        redis_connection = get_redis_connection()
        redis_connection.hdel(REDIS_PASSWORD_RESET_KEY, key)

    @classmethod
    def reset_email(cls, email, request):

        user_exists = cls.objects.filter(email__iexact=email).exists()

        if user_exists:
            user = cls.objects.get(email__iexact=email)
            user.send_reset_password_email(request)
        else:
            # Do nothing if the email does not exist so
            # that you cannot enumerate the emails
            pass

    @classmethod
    def check_reset_key(cls, key, max_age=MAX_PASSWORD_RESET_SECONDS):
        return cls.check_key(key, PASSWORD_RESET_SALT, max_age, REDIS_PASSWORD_RESET_KEY)

    @classmethod
    def check_activation_key(cls, key, max_age=MAX_ACTIVATION_SECONDS):
        return cls.check_key(key, ACCOUNT_ACTIVATION_SALT, max_age, REDIS_ACCOUNT_ACTIVATION_KEY)

    @classmethod
    def check_key(cls, key, salt, max_age, redis_key):
        try:
            user_data = signing.loads(key, salt=salt, max_age=max_age)

            email = user_data["email"]
            try:
                user = cls.objects.get(email__iexact=email)
                redis_connection = get_redis_connection()
                raw_payload = redis_connection.hget(redis_key, email)
                if raw_payload:
                    payload = json.loads(raw_payload)
                    if payload["key"] == key:
                        return user, ""
                    return None, "Key invalid or expired"
                return None, "No Key found"
            except cls.DoesNotExist:
                return None, "No such user"
        except BadSignature:
            return None, "Bad Signature"

    def send_account_activation_email(self, request):

        key = signing.dumps({"email": self.email}, salt=ACCOUNT_ACTIVATION_SALT)

        url = request.build_absolute_uri(f"/activate/{key}")

        redis_connection = get_redis_connection()
        payload = json.dumps({"key": key}).encode("utf-8")
        redis_connection.hset(REDIS_ACCOUNT_ACTIVATION_KEY, self.email, payload)

        message = emails.ACCOUNT_ACTIVATION.format(expiration=f"{MAX_ACTIVATION_HOURS} hours", url=url)

        subject = f"Account Activation for {self.email}"

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email])

    @classmethod
    def email_exists(cls, email):
        return cls.objects.filter(email__iexact=email).exists()

    @classmethod
    def create_inactive_user(cls, user_data):
        return cls.objects.create_user(
            email=user_data["email"],
            password=user_data["password1"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            is_active=False,
        )


class ApiKey(IndexedTimeStampedModel):
    KEY_LENGTH = 64
    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="api_keys",
        on_delete=models.PROTECT,
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return secrets.token_hex(cls.KEY_LENGTH)[0 : cls.KEY_LENGTH]

    def __str__(self):
        return f"AuthKey for {self.user}"
