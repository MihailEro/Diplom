from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.create(
            phone='+79518295911',
            first_name='Miha',
            last_name='Miha',
            is_staff=True,
            is_superuser=True,
        )
        user.set_password('1234')
        user.save()
