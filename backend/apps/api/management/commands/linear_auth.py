import os
import webbrowser
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Open the Linear OAuth login page in your browser.'

    def handle(self, *args, **options):
        client_id = os.getenv('LINEAR_CLIENT_ID')
        
        if not client_id:
            self.stdout.write(self.style.ERROR('LINEAR_CLIENT_ID is not set in your .env file.'))
            return

        # Use the same configuration as in views.py
        redirect_uri = "http://localhost:8000/api/v1/auth/linear/callback"
        scope = "read write"
        
        auth_url = (
            f"https://linear.app/oauth/authorize?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"scope={scope}"
        )

        self.stdout.write(self.style.SUCCESS(f'Opening Linear OAuth login page:'))
        self.stdout.write(auth_url)
        
        # Open in the default web browser
        webbrowser.open(auth_url)
        
        self.stdout.write(self.style.WARNING('\nOnce you have authenticated, the browser will redirect you to a page displaying an authorization code.'))
        self.stdout.write(self.style.WARNING(f'Redirect target: {redirect_uri}'))
        self.stdout.write(self.style.WARNING('Copy that code and you will be ready to exchange it for an access token.'))
