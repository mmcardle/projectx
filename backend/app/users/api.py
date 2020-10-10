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

from validation.base import load_data_from_schema
from validation.exceptions import SchemaError

from . import models, validation

logger = logging.getLogger(__name__)

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
            "user": request.user.to_json(include_connections=True),
            "token": _get_token(request),
            "logout_url": _get_logout_url(request)
        })
    else:
        return JsonResponse({"user": None}, status=401)


@ratelimit(key="user_or_ip", rate="5/m", method=ratelimit.UNSAFE, block=True)
def login(request):
    if request.method == "POST":
        content = json.loads(request.body)
        username = content.get("username")
        password = content.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            django_login(request, user)
            return JsonResponse({
                "success": True,
                "user": user.to_json(include_connections=True),
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

    return JsonResponse({"email": user.email, "username": user.username})


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


@csrf_exempt
def remote_check(request):
    # This method checks the IP of the request is in the Sohonet IP space
    # OR the remote ip of the user specified on a staff user object
    # OR the session has been SUDO'd into and the user is trying to exit SU

    original_uri = request.META.get("X-Original-URI")
    is_sudo = _request_is_sudo(request)
    if is_sudo and original_uri == reverse(admin_su_logout):
        return HttpResponse(status=200)

    remote_addr = request.META.get("REMOTE_ADDR")
    if not remote_addr:
        logger.warning("Could not fetch remote address 'REMOTE_ADDR' in request, access DENIED.")
        return HttpResponse(status=403)

    if not request.user.is_anonymous:
        if request.user.is_staff and request.user.remote_allowed_cidrs:
            for remote_allowed_cidr in request.user.remote_allowed_cidrs:
                valid_network = ipaddress.ip_network(remote_allowed_cidr)
                valid_by_user_remote_ip = ipaddress.ip_address(remote_addr) in valid_network
                if valid_by_user_remote_ip:
                    logger.debug(
                        f"The user is staff and the IP {remote_addr} is in {valid_network}, "
                        f"access granted. (Allowed by user.remote_allowed_cidrs)"
                    )
                    return HttpResponse(status=200)

    ALLOWED_REMOTE_IP_RANGES = [
        "67.224.101.0/26",    # US-DCN-UNTRUST
        "67.224.101.64/29",   # US-OFFICE-UNTRUST
        "193.203.71.176/29",  # POLST-DCN-UNTRUST
        "193.203.71.224/29",  # GSW-DCN-UNTRUST
        "193.203.87.176/28",  # LPC-DCN-UNTRUST
        "193.203.88.16/28",   # LPC-DCN-DMZ
        "46.248.224.132/32",  # Sohonet UK Internal Office Network
        "193.203.89.154/32",  # UK Dev SSL VPN
    ]

    if settings.DEBUG:
        ALLOWED_REMOTE_IP_RANGES.extend([
            "192.168.0.0/16",    # Dev
            "172.16.0.0/12",     # Dev
            "10.0.0.0/8",        # Dev
            "127.0.0.1",         # Local
        ])

    for ip_range in ALLOWED_REMOTE_IP_RANGES:
        valid = ipaddress.ip_address(remote_addr) in ipaddress.ip_network(ip_range)
        if valid:
            logger.debug(f"The IP {remote_addr} is in {ip_range}, access granted.")
            return HttpResponse(status=200)

    logger.warning(f"The IP {remote_addr} is not in {ALLOWED_REMOTE_IP_RANGES}, access DENIED.")

    return HttpResponse(status=403)


def admin_su_logout(request):

    su_response = su_logout(request)

    if su_response.status_code > 400:
        return JsonResponse({"error": su_response.content}, status=su_response.status_code)

    return JsonResponse({"redirect_url": su_response.url})