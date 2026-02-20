import os
import requests
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create a Linear Issue from the CLI.'

    def add_arguments(self, parser):
        parser.add_argument('--title', type=str, required=True, help='Issue Title')
        parser.add_argument('--desc', type=str, help='Issue Description')
        parser.add_argument('--team', type=str, help='Linear Team ID (if not set in .env)')
        parser.add_argument('--priority', type=int, default=0, help='Issue Priority (0-4)')

    def handle(self, *args, **options):
        # 1. Get Access Token
        token = os.getenv('LINEAR_ACCESS_TOKEN')
        if not token:
            self.stdout.write(self.style.ERROR('LINEAR_ACCESS_TOKEN is not set in your .env file.'))
            self.stdout.write(self.style.WARNING('Please run `python manage.py linear-auth` first to get your code.'))
            return

        # 2. Get Team ID
        team_id = options['team'] or os.getenv('LINEAR_TEAM_ID')
        if not team_id:
            self.stdout.write(self.style.ERROR('LINEAR_TEAM_ID is not set in your .env file.'))
            return

        # 3. Create Issue via GraphQL API
        title = options['title']
        description = options['desc'] or ""
        priority = options['priority']

        query = """
        mutation IssueCreate($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                success
                issue {
                    id
                    url
                    identifier
                    title
                }
            }
        }
        """

        variables = {
            "input": {
                "title": title,
                "description": description,
                "teamId": team_id,
                "priority": priority
            }
        }

        url = "https://api.linear.app/graphql"
        headers = {
            "Content-Type": "application/json",
            "Authorization": token  # No Bearer prefix for Linear Personal Tokens, but for OAuth it's required
        }
        
        # If it's an OAuth token, it usually needs "Bearer "
        if not token.startswith("lin_api_"): # Heuristic to check if it's OAuth or Personal Token
             headers["Authorization"] = f"Bearer {token}"

        response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if result.get('data') and result['data']['issueCreate']['success']:
                issue = result['data']['issueCreate']['issue']
                self.stdout.write(self.style.SUCCESS(f"Successfully created Issue: {issue['identifier']} - {issue['title']}"))
                self.stdout.write(self.style.SUCCESS(f"URL: {issue['url']}"))
            else:
                self.stdout.write(self.style.ERROR(f"Failed to create issue: {result.get('errors')}"))
        else:
            self.stdout.write(self.style.ERROR(f"HTTP Error: {response.status_code} - {response.text}"))
