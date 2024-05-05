"""
Django command to wait for the database to be available.
"""
import time

from psycopg2 import OperationalError as Psycopg2Error

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args, **kwargs):
        """Entrypoint for command."""
        self.stdout.write('Waiting for db...')
        db = False
        while db is False:
            try:
                self.check(databases=['default'])
                db = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write('Unavailable db, waiting...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Available db!'))
