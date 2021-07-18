import time

from django.core.management.base import BaseCommand
from django.db import connection
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = "Check DB connection"

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database connection...")
        db_conn = None
        count = 0
        sleep_seconds = 1
        while not db_conn and count < 120:
            try:
                connection.ensure_connection()
                db_conn = True
            except OperationalError:
                self.stdout.write(f"Database unavailable, waiting ${sleep_seconds}s...")
                count += 1
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Database available!"))
