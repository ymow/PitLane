import os
import requests
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Update a Linear Issue status or description.'

    def add_arguments(self, parser):
        parser.add_argument('issue_id', type=str, help='Issue Identifier (e.g., PL-6)')
        parser.add_argument('--status', type=str, help='New Status Name (e.g., Done, In Progress)')
        parser.add_argument('--desc', type=str, help='Append to Description')

    def handle(self, *args, **options):
        token = os.getenv('LINEAR_ACCESS_TOKEN')
        if not token:
            self.stdout.write(self.style.ERROR('LINEAR_ACCESS_TOKEN not set.'))
            return

        issue_id = options['issue_id']
        
        # 1. Fetch the Issue and available States first to find the ID
        query_info = """
        query {
          issue(id: "%s") {
            id
            team {
              states {
                id
                name
              }
            }
          }
        }
        """ % issue_id

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}" if not token.startswith("lin_api_") else token
        }

        response = requests.post("https://api.linear.app/graphql", json={"query": query_info}, headers=headers)
        if response.status_code != 200:
            self.stdout.write(self.style.ERROR(f"Error: {response.text}"))
            return

        res_data = response.json()
        issue_data = res_data.get('data', {}).get('issue')
        if not issue_data:
            self.stdout.write(self.style.ERROR(f"Issue {issue_id} not found."))
            return

        target_state_id = None
        if options['status']:
            for state in issue_data['team']['states']:
                if state['name'].lower() == options['status'].lower():
                    target_state_id = state['id']
                    break
            
            if not target_state_id:
                available = ", ".join([s['name'] for s in issue_data['team']['states']])
                self.stdout.write(self.style.ERROR(f"Status '{options['status']}' not found. Available: {available}"))
                return

        # 2. Execute Update
        mutation = """
        mutation IssueUpdate($id: String!, $input: IssueUpdateInput!) {
          issueUpdate(id: $id, input: $input) {
            success
            issue {
              id
              identifier
              state { name }
            }
          }
        }
        """
        
        variables = {
            "id": issue_data['id'],
            "input": {}
        }
        
        if target_state_id:
            variables["input"]["stateId"] = target_state_id
        if options['desc']:
            variables["input"]["description"] = options['desc']

        resp = requests.post("https://api.linear.app/graphql", json={"query": mutation, "variables": variables}, headers=headers)
        
        if resp.status_code == 200:
            result = resp.json()
            if result.get('data') and result['data']['issueUpdate']['success']:
                issue = result['data']['issueUpdate']['issue']
                self.stdout.write(self.style.SUCCESS(f"Successfully updated {issue['identifier']}!"))
                self.stdout.write(self.style.SUCCESS(f"Current Status: {issue['state']['name']}"))
            else:
                self.stdout.write(self.style.ERROR(f"Update failed: {result.get('errors')}"))
        else:
            self.stdout.write(self.style.ERROR(f"HTTP Error: {resp.status_code}"))
