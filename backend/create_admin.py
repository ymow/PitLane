import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = 'admin2'
email = 'admin2@pitlane.com'
password = 'admin123'

if User.objects.filter(username=username).exists():
    print(f'User "{username}" already exists.')
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser "{username}" created successfully!')
    print(f'Username: {username}')
    print(f'Email: {email}')
    print(f'Password: {password}')
    print('\nYou can now log in to the admin panel at /admin/')
