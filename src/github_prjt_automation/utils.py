import requests
import json
import yaml
import os


def load_yaml(file_path="config.yaml"):
    try:
        with open(file_path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        return {}


def get_config():
    config = load_yaml()

    # Fallbacks to env vars
    config["github_token"] = os.getenv("GITHUB_TOKEN") or config.get("github_token")
    config["repo_owner"] = config.get("repo_owner") or os.getenv("REPO_OWNER")
    config["repo_name"] = config.get("repo_name") or os.getenv("REPO_NAME")
    config["repo"] = config.get("repo") or f'{config["repo_owner"]}/{config["repo_name"]}'
    config["project_name"] = config.get("project_name") or os.getenv("PROJECT_NAME")

    config["issues"] = config.get("issues", [])
    return config


class GitHubHelper:
    """
    A helper class to interact with the GitHub GraphQL and REST APIs
    for managing issues and projects.
    """
    def __init__(self, token: str, repo: str):
        self.token = token
        self.repo = repo
        self.project_id = None
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }

    def _graphql_query(self, query: str, variables: dict = None) -> dict:
        url = "https://api.github.com/graphql"
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()["data"]

    def get_or_create_project(self, project_title: str) -> str:
        query = """
        query {
            viewer {
                projectsV2(first: 10) {
                    nodes {
                        title
                        id
                    }
                }
            }
        }
        """
        data = self._graphql_query(query)
        projects = data["viewer"]["projectsV2"]["nodes"]
        for project in projects:
            if project["title"] == project_title:
                print(f"✅ Project '{project_title}' exists.")
                self.project_id = project["id"]
                return self.project_id

        print(f"❌ Project '{project_title}' not found. Creating...")
        return self.create_project(project_title)

    def create_project(self, project_title: str) -> str:
        mutation = """
        mutation($title: String!) {
            createProjectV2(input: {title: $title, ownerId: "MDQ6VXNlcjU4NTYz"}) {
                projectV2 {
                    id
                }
            }
        }
        """
        variables = {"title": project_title}
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": mutation, "variables": variables},
            headers=self.headers
        )
        response.raise_for_status()
        project_id = response.json()["data"]["createProjectV2"]["projectV2"]["id"]
        self.project_id = project_id
        print(f"✅ Created project '{project_title}' with ID {project_id}")
        return project_id

    def create_issue(self, title: str) -> dict:
        url = f"https://api.github.com/repos/{self.repo}/issues"
        payload = {"title": title}
        response = requests.post(url, json=payload, headers=self.headers)
        if response.status_code == 201:
            return response.json()
        print(f"❌ Failed to create issue: {response.text}")
        return None

    def add_issue_to_project(self, project_id: str, issue_id: str) -> bool:
        mutation = """
        mutation($projectId: ID!, $contentId: ID!) {
            addProjectV2ItemById(input: {
                projectId: $projectId,
                contentId: $contentId
            }) {
                item {
                    id
                }
            }
        }
        """
        variables = {"projectId": project_id, "contentId": issue_id}
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": mutation, "variables": variables},
            headers=self.headers
        )
        if response.status_code == 200:
            return True
        print(f"❌ Failed to add issue to project: {response.text}")
        return False

    def get_status_field_id(self, status: str) -> tuple:
        query = """
        query($projectId: ID!) {
            node(id: $projectId) {
                ... on ProjectV2 {
                    fields(first: 20) {
                        nodes {
                            ... on ProjectV2SingleSelectField {
                                id
                                name
                                options {
                                    id
                                    name
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        variables = {"projectId": self.project_id}
        data = self._graphql_query(query, variables)
        fields = data["node"]["fields"]["nodes"]
        for field in fields:
            if field["name"] == "Status":
                for option in field["options"]:
                    if option["name"] == status:
                        return field["id"], option["id"]
        return None, None

    def set_issue_status(self, issue_number: int, status: str, project_id: str) -> bool:
        try:
            field_id, option_id = self.get_status_field_id(status)
            item_id = self._get_project_item_id(project_id, issue_number)
            if not item_id:
                print("❌ Could not find project item ID.")
                return False

            mutation = """
            mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
                updateProjectV2ItemFieldValue(input: {
                    projectId: $projectId,
                    itemId: $itemId,
                    fieldId: $fieldId,
                    value: {
                        singleSelectOptionId: $optionId
                    }
                }) {
                    projectV2Item {
                        id
                    }
                }
            }
            """
            variables = {
                "projectId": project_id,
                "itemId": item_id,
                "fieldId": field_id,
                "optionId": option_id,
            }
            response = requests.post(
                "https://api.github.com/graphql",
                json={"query": mutation, "variables": variables},
                headers=self.headers
            )
            if response.status_code == 200:
                return True
            print(f"❌ Failed to set status: {response.text}")
            return False
        except Exception as e:
            print(f"❌ Exception when setting status: {e}")
            return False

    def _get_project_item_id(self, project_id: str, issue_number: int) -> str:
        query = """
        query($projectId: ID!) {
            node(id: $projectId) {
                ... on ProjectV2 {
                    items(first: 100) {
                        nodes {
                            id
                            content {
                                ... on Issue {
                                    number
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        variables = {"projectId": project_id}
        data = self._graphql_query(query, variables)
        items = data["node"]["items"]["nodes"]
        for item in items:
            if item["content"] and item["content"]["number"] == issue_number:
                return item["id"]
        return None
