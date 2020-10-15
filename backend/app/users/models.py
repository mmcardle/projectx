import uuid
import calendar
import json
import logging

from asgiref.sync import AsyncToSync
from channels.layers import get_channel_layer
from common.models import IndexedTimeStampedModel
from django.core import signing
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.core.signing import BadSignature
from django_redis import get_redis_connection

from . import emails

logger = logging.getLogger(__name__)

REDIS_PASSWORD_RESET_KEY = "password_reset"

ACTIVATION_SALT = "account_activation"
PASSWORD_RESET_SALT = "password_reset"

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

    email = models.EmailField(max_length=255, unique=True)
    public_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()
    
    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email
    
    def __str__(self):
        return "%s" % self.display_name()
    
    @property
    def public_id(self):
        return str(self.public_uuid)

    def role(self):
        return "admin" if self.is_staff else "user"

    def unique_name(self):
        return "%s_%s" % (
            self.email.replace("@", "_").replace(".", "_"),
            self.public_id[0:8],
        )

    def display_name(self):
        return self.get_full_name()

    def to_json(self):
        data = {
            "role": self.role(),
            "public_id": self.public_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "display_name": self.display_name(),
            "email": self.email,
            "last_login_timestamp": self._last_login_timestamp(),
            "last_login_timestamp_iso": self._last_login_timestamp_iso(),
        }

        return data

    def _last_login_timestamp(self):
        if self.last_login:
            return calendar.timegm(self.last_login.utctimetuple())

    def _last_login_timestamp_iso(self):
        if self.last_login:
            return self.last_login.isoformat()

    def activate(self):
        self.is_active = True
        self.save()

    def reset_password(self):

        key = signing.dumps(
            {"email": self.email}, salt=PASSWORD_RESET_SALT
        )

        redis_connection = get_redis_connection()
        payload = json.dumps({"key": key}).encode("utf-8")
        redis_connection.hset(
            REDIS_PASSWORD_RESET_KEY,
            self.email,
            payload
        )

        url = "/password_reset/%s" % key

        schema = "http" if settings.DEBUG else "https"
        port = ":8000" if settings.DEBUG else ""

        message = emails.reset_password.format(
            title="ProjectX Password Reset",
            expiration="%s hours" % MAX_PASSWORD_RESET_HOURS,
            schema=schema,
            site=settings.PUBLIC_IP,
            port=port,
            url=url
        )

        subject = "Password Reset for %s" % self.email

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.email]
        )

    def send_data_to_user(self, data):
        payload = json.dumps(data)
        AsyncToSync(get_channel_layer().group_send)(
            self.unique_name(), {"type": "user.message", "data": payload}
        )

    @classmethod
    def delete_reset_key(cls, key):
        redis_connection = get_redis_connection()
        redis_connection.hdel(REDIS_PASSWORD_RESET_KEY, key)

    @classmethod
    def email_in_error(cls, email):
        """
        If we get to here there are multiple users with emails
        with different cases e.g. (USER@example.com, user@example.com)
        We try to prevent this at registration but it is possible
        the user has been editted (in the admin)
        So lets alart on the exception but still send the email to
        all the addresses.
        """
        logger.exception(
            "Multiple users with the same case insensitive email %s"
            % email
        )

    @classmethod
    def reset_email(cls, email):

        user_exists = cls.objects.filter(
            email__iexact=email
        ).exists()

        try:
            if user_exists:
                user = cls.objects.get(email__iexact=email)
                user.reset_password()
            else:
                # Do nothing if the email does not exist so
                # that you cannot enumerate the emails
                pass
        except cls.MultipleObjectsReturned:
            cls.email_in_error(email)
            users = cls.objects.filter(email__iexact=email)
            for user in users:
                user.reset_password()

    @classmethod
    def check_reset_key(cls, key):
        try:
            user_data = signing.loads(
                key, salt=PASSWORD_RESET_SALT,
                max_age=MAX_PASSWORD_RESET_SECONDS
            )

            email = user_data["email"]
            try:
                user = cls.objects.get(email__iexact=email)
                redis_connection = get_redis_connection()
                raw_payload = redis_connection.hget(REDIS_PASSWORD_RESET_KEY, email)
                if raw_payload:
                    payload = json.loads(raw_payload)
                    if payload["key"] == key:
                        return user, ""
                    else:
                        return None, "Password Reset key invalid or expired"
                else:
                    return None, "No Password Reset key found"
            except cls.DoesNotExist:
                return None, "No such user"
            except cls.MultipleObjectsReturned:
                cls.email_in_error(email)
                user = cls.objects.filter(email__iexact=email).first()
                return user, ""
        except BadSignature:
            return None, "Bad Signature"

    @classmethod
    def check_activation_key(cls, key, max_age=MAX_ACTIVATION_SECONDS):
        try:
            user_data = signing.loads(
                key, salt=ACTIVATION_SALT,
                max_age=max_age
            )
            try:
                user = cls.objects.get(email=user_data["email"])
                return user, ""
            except cls.DoesNotExist:
                return None, "No such user"
        except BadSignature:
            return None, "Bad Signature"

    def send_activation_email(self, request):

        key = signing.dumps(
            {"email": self.email}, salt=ACTIVATION_SALT
        )

        url = request.build_absolute_uri("/activate/%s" % key)

        message = emails.account_activation.format(
            expiration="%s hours" % MAX_ACTIVATION_HOURS,
            url=url
        )

        subject = "Activate email %s" % self.email

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.email]
        )

    @classmethod
    def create_inactive_user(cls, user_data):
        user = cls.objects.create_user(
            email=user_data["email"],
            password=user_data["password1"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            is_active=False
        )
        return user