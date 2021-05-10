import json
import logging

from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template import engines
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django_su.views import su_logout
from ratelimit.decorators import ratelimit

from users import decorators, models

logger = logging.getLogger(__name__)


def _get_token(request):
    template = engines["django"].from_string("{{ csrf_token }}")
    return template.render(request=request)


def _request_is_sudo(request):
    return len(request.session.get("exit_users_pk", default=[])) > 0


def _get_logout_url(request):
    if _request_is_sudo(request):
        return reverse("admin_su_logout")
    return reverse("user_api_logout")


def user_details(request):
    if request.user.is_authenticated:
        return JsonResponse(
            {"user": request.user.to_json(), "token": _get_token(request), "logout_url": _get_logout_url(request)}
        )
    return JsonResponse({"user": None})


@ratelimit(key="user_or_ip", rate="5/m", method=ratelimit.UNSAFE, block=True)
def login(request):
    if request.method == "POST":
        content = json.loads(request.body)
        email = content.get("email")
        password = content.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            django_login(request, user)
            return JsonResponse(
                {
                    "success": True,
                    "user": user.to_json(),
                    # new csrf token will have been created
                    "token": request.META["CSRF_COOKIE"],
                    "logout_url": _get_logout_url(request),
                }
            )
        return JsonResponse({"success": False}, status=401)
    return JsonResponse({"token": _get_token(request)})


@login_required
def logout(request):
    django_logout(request)
    return JsonResponse({"success": True})


@require_http_methods(["POST"])
@decorators.register_payload
def register(request):

    email = request.validated_data.get("email")
    existing_user = models.User.email_exists(email)

    if existing_user:
        errors = {"email": ["This email is already registered"]}
        return JsonResponse({"error": True, "errors": errors}, status=401)

    new_user = models.User.create_inactive_user(request.validated_data)
    new_user.send_account_activation_email(request)

    return JsonResponse(new_user.to_json())


@require_http_methods(["POST"])
@ratelimit(key="user_or_ip", rate="5/m", method=ratelimit.UNSAFE, block=True)
@decorators.reset_password_payload
def reset_password(request):

    email = request.validated_data["email"]
    if models.User.email_exists(email):
        models.User.reset_email(email, request)
    else:
        # Do nothing different to prevent email enumeration
        pass

    return JsonResponse({})


@require_http_methods(["POST"])
@ratelimit(key="user_or_ip", rate="5/m", method=ratelimit.UNSAFE, block=True)
@decorators.reset_password_complete_payload
def reset_password_complete(request):

    reset_data = request.validated_data
    key = reset_data.get("reset_key")

    user, error = models.User.check_reset_key(key)
    if user is None:
        return JsonResponse({"error": error}, status=401)

    user.set_password(reset_data.get("password1"))
    user.save()

    # Key can only be used once
    user.delete_reset_key(user.email)

    return JsonResponse(user.to_json())


@login_required
@require_http_methods(["POST"])
@ratelimit(key="user_or_ip", rate="5/m", method=ratelimit.UNSAFE, block=True)
@decorators.change_password_payload
def change_password(request):

    current_password = request.validated_data["current_password"]
    user = authenticate(username=request.user.email, password=current_password)
    if user is not None:
        password1 = request.validated_data["password1"]
        user.set_password(password1)
        user.save()
        update_session_auth_hash(request, user)
    else:
        return JsonResponse(
            {"error": True, "errors": {"current_password": ["The current password is incorrect."]}}, status=401
        )

    return JsonResponse({})


@login_required
@require_http_methods(["POST"])
@ratelimit(key="user_or_ip", rate="5/m", method=ratelimit.UNSAFE, block=True)
@decorators.change_details_payload
def change_details(request):

    change_details_data = request.validated_data

    user = request.user
    user.first_name = change_details_data["first_name"]
    user.last_name = change_details_data["last_name"]
    user.save()

    return JsonResponse({})


@require_http_methods(["POST"])
@ratelimit(key="user_or_ip", rate="5/m", method=ratelimit.UNSAFE, block=True)
@decorators.reset_password_check_payload
def reset_password_check(request):

    key = request.validated_data.get("reset_key")

    user, error = models.User.check_reset_key(key)
    if user is None:
        return JsonResponse({"error": error}, status=401)

    return JsonResponse({"email": user.email})


@require_http_methods(["POST"])
@ratelimit(key="user_or_ip", rate="5/m", method=ratelimit.UNSAFE, block=True)
@decorators.activate_payload
def activate(request):

    user = request.validated_data["user"]
    user.activate()

    return JsonResponse({"is_active": user.is_active, "user": user.to_json()})


def admin_su_logout(request):

    su_response = su_logout(request)

    if su_response.status_code > 400:
        return JsonResponse({"error": su_response.content}, status=su_response.status_code)

    return JsonResponse({"redirect_url": su_response.url})
