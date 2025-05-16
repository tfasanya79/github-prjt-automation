import os

from .utils import GitHubHelper, load_yaml


def main():
    config_path = os.path.join(os.path.dirname(__file__), '../../config.yaml')
    config = load_yaml(config_path)

    github_token = os.getenv("GITHUB_TOKEN") or config.get("GITHUB_TOKEN")
    if not github_token:
        raise EnvironmentError("GitHub token not found. Set GITHUB_TOKEN environment variable or add to config.yaml")

    gh = GitHubHelper(
        token=config["GITHUB_TOKEN"],
        repo=config["repo"]
    )
    project_id = gh.get_or_create_project(config["project_title"])

    if not project_id:
        print(f"❌ Project '{gh.project_title}' not found.")
        return    
    print(f"✅ Project '{config['project_title']}' exists.")


    for issue_data in config["issues"]:
        issue_title = issue_data["title"]
        issue = gh.create_issue(issue_title)
        if not issue:
            print(f"❌ Failed to create issue '{issue_title}'")
            continue

        issue_id = issue["id"]
        issue_number = issue["number"]
        gh.add_issue_to_project(project_id, issue_id)
        gh.set_issue_status(project_id, issue_number, "Todo")


if __name__ == "__main__":
    main()
