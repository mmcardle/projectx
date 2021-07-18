from django.core.management.base import BaseCommand

from projectx.users.models import User


class Command(BaseCommand):
    help = "Create a user"

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            help="Specifies the login.",
        )
        parser.add_argument(
            "--password",
            dest="password",
            default=None,
            help="Specifies the password.",
        )

    def handle(self, *args, **options):
        password = options.get("password")
        email = options.get("email")

        if not email:
            raise Exception("Email is required")
        if not password:
            raise Exception("Password is required")

        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            self.stdout.write(self.style.SUCCESS("User already exists"))
        except User.DoesNotExist:
            user = User.objects.create_user(email, password=password)
            self.stdout.write(self.style.SUCCESS("User created"))

        user.active = True
        user.save()

        self.stdout.write(self.style.SUCCESS("Test User Updated"))
