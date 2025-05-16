# src/github_prjt_automation/utils.py

import requests
import logging
import yaml

def load_yaml(config_file: str) -> dict:
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)



logger = logging.getLogger("github_prjt_automation")

GITHUB_API = "https://api.github.com"
GRAPHQL_API = "https://api.github.com/graphql"

class GitHubHelper:
    def __init__(self, token, repo):
        self.token = token
        self.repo = repo
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
        }

    def get_status_field_id(self, project_id):
        logger.info(f"ℹ️ Placeholder: get_status_field_id({project_id}) called.")
        return "fake-status-field-id"

    def set_status_field(self, project_id, issue_node_id, field_id, status_value):
        logger.info(f"ℹ️ Placeholder: set_status_field({project_id}, {issue_node_id}, {field_id}, {status_value}) called.")

    def get_project_by_name(self, name):
        logger.info(f"ℹ️ Placeholder: get_project_by_name({name}) called.")
        return {"id": "MOCK_PROJECT_ID", "title": name}


    def _graphql_query(self, query, variables=None):
        response = requests.post(
            GRAPHQL_API,
            json={"query": query, "variables": variables or {}},
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json()["data"]

    def get_or_create_project(self, project_title):
        query = """
        query {
            viewer {
                projectsV2(first: 100) {
                    nodes {
                        id
                        title
                    }
                }
            }
        }
        """
        data = self._graphql_query(query)
        projects = data["viewer"]["projectsV2"]["nodes"]
        for project in projects:
            if project["title"] == project_title:
                logger.info(f"✅ Project '{project_title}' already exists.")
                return project["id"]
        raise ValueError(f"Project '{project_title}' not found. Auto-creation not implemented.")

    def create_issue(self, title, body=""):
        url = f"{GITHUB_API}/repos/{self.repo}/issues"
        payload = {"title": title, "body": body}
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        issue = response.json()
        logger.info(f"📝 Issue '{title}' created.")
        return issue["node_id"]

    def add_issue_to_project(self, project_id, issue_node_id):
        mutation = """
        mutation($projectId:ID!, $contentId:ID!) {
            addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
                item {
                    id
                }
            }
        }
        """
        variables = {"projectId": project_id, "contentId": issue_node_id}
        self._graphql_query(mutation, variables)
        logger.info("✔️ Issue added to project.")

    def set_issue_status(self, project_id, issue_node_id, status="Todo"):
        # In practice, you'd retrieve the status field ID and match to options.
        logger.info(f"✅ Status set to '{status}' (Placeholder - refine this logic in production)")


def load_issues_from_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)
