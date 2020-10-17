import ipaddress
import json
import logging

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.http import HttpResponse, JsonResponse
from django.template import engines
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django_su.views import su_logout
from ratelimit.decorators import ratelimit

from common.validation import SchemaError, load_data_from_schema

from . import models, validation

logger = logging.getLogger(__name__)

register_schema = validation.RegisterSchema()
reset_password_schema = validation.ResetPasswordSchema()
reset_check_schema = validation.ResetCheckSchema()


def _get_token(request):
    template = engines["django"].from_string("{{ csrf_token }}")
    return template.render(request=request)


def _request_is_sudo(request):
    return len(request.session.get("exit_users_pk", default=[])) > 0


def _get_logout_url(request):
    if _request_is_sudo(request):
        return reverse("admin_su_logout")
    else:
        return reverse("user_api_logout")


def user(request):
    if request.user.is_authenticated:
        return JsonResponse({
            "user": request.user.to_json(),
            "token": _get_token(request),
            "logout_url": _get_logout_url(request)
        })
    else:
        return JsonResponse({"user": None}, status=401)


@ratelimit(key="user_or_ip", rate="5/m", method=ratelimit.UNSAFE, block=True)
def login(request):
    if request.method == "POST":
        content = json.loads(request.body)
        email = content.get("email")
        password = content.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            django_login(request, user)
            return JsonResponse({
                "success": True,
                "user": user.to_json(),
                # new csrf token will have been created
                "token": request.META["CSRF_COOKIE"],
                "logout_url": _get_logout_url(request)
            })
        else:
            return JsonResponse({"success": False}, status=401)
    else:
        return JsonResponse({"token": _get_token(request)})


def logout(request):
    django_logout(request)
    return JsonResponse({"success": True})


@require_http_methods(["POST"])
def activate(request):

    payload = json.loads(request.body)
    key = payload.get("activation_key")

    if key is None:
        return JsonResponse(
            {"error": "No key in post body"}, status=401
        )

    user, error = models.User.check_activation_key(key)
    if user is None:
        # User has failed activation check
        # Check if the token has expired
        expired_user, expired_error = models.User.check_activation_key(
            key, max_age=None
        )
        if expired_user:
            logger.error(expired_error)
            expired_user.send_activation_email(request)
            return JsonResponse({
                "error": (
                    "That token has expired. A new email has been sent"
                    "to your address. PLease click on the new "
                    "link in the email."
                ),
            }, status=401)

        return JsonResponse({"error": error}, status=401)

    if user.is_active:
        return JsonResponse(
            {
                "is_active": True,
                "error": "User is already active."
            },
            status=400
        )
    else:
        user.activate()

    return JsonResponse(user.to_json())


@require_http_methods(["POST"])
def register(request):

    try:
        register_data = load_data_from_schema(
            register_schema, json.loads(request.body)
        )
    except SchemaError as e:
        return JsonResponse(
            {"error": True, "errors": e.errors}, status=401
        )

    existing_user = models.User.objects.filter(
        email__iexact=register_data.get("email")
    ).exists()

    if existing_user:
        errors = {"email": ["This email is already registered"]}
        return JsonResponse(
            {"error": True, "errors": errors}, status=401
        )

    new_user = models.User.create_inactive_user(register_data)
    new_user.send_activation_email(request)

    return JsonResponse(new_user.to_json())

@require_http_methods(["POST"])
@ratelimit(key="user_or_ip", rate="5/m", method=ratelimit.UNSAFE, block=True)
def reset_password(request):

    try:
        email = json.loads(request.body)["email"]
    except (json.decoder.JSONDecodeError, KeyError):
        logger.exception("Reset Password Failure")
        return JsonResponse({"error": True}, status=401)

    models.User.reset_email(email)

    return JsonResponse({})


@require_http_methods(["POST"])
@ratelimit(key="user_or_ip", rate="5/m", method=ratelimit.UNSAFE, block=True)
def reset_password_check(request):

    try:
        reset_check_validation = load_data_from_schema(
            reset_check_schema, json.loads(request.body)
        )
    except SchemaError as e:
        return JsonResponse(
            {"error": True, "errors": e.errors}, status=401
        )

    reset_data = reset_check_validation
    key = reset_data.get("reset_key")

    user, error = models.User.check_reset_key(key)
    if user is None:
        return JsonResponse({"error": error}, status=401)

    return JsonResponse({"email": user.email})


@require_http_methods(["POST"])
@ratelimit(key="user_or_ip", rate="5/m", method=ratelimit.UNSAFE, block=True)
def reset_password_complete(request):

    try:
        reset_complete_validation = load_data_from_schema(
            reset_password_schema, json.loads(request.body)
        )
    except SchemaError as e:
        return JsonResponse(
            {"error": True, "errors": e.errors}, status=401
        )

    reset_data = reset_complete_validation
    key = reset_data.get("reset_key")

    user, error = models.User.check_reset_key(key)
    if user is None:
        return JsonResponse({"error": error}, status=401)

    user.set_password(reset_data.get("password1"))
    user.save()

    # Key can only be used once
    user.delete_reset_key(user.email)

    return JsonResponse(user.to_json())

def admin_su_logout(request):

    su_response = su_logout(request)

    if su_response.status_code > 400:
        return JsonResponse({"error": su_response.content}, status=su_response.status_code)

    return JsonResponse({"redirect_url": su_response.url})
