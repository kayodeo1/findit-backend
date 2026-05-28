import os

from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = "Create or update an admin user from ADMIN_EMAIL / ADMIN_PASSWORD env vars."

    def handle(self, *args, **options):
        email = (os.environ.get("ADMIN_EMAIL") or "").strip().lower()
        password = os.environ.get("ADMIN_PASSWORD") or ""

        if not email or not password:
            self.stdout.write("ADMIN_EMAIL/ADMIN_PASSWORD not set — skipping admin creation.")
            return

        user, created = User.objects.get_or_create(
            email=email,
            defaults={"username": email},
        )
        user.username = user.username or email
        user.role = User.Role.ADMIN
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} admin account: {email}"))
