import os
from .utils import GitHubHelper, get_config


def main():
    config = get_config()
    print("CONFIG:", get_config())


    if not config.get("github_token"):
        raise EnvironmentError("GitHub token not found. Set GITHUB_TOKEN or add it to config.yaml")

    helper = GitHubHelper(token=config["github_token"], repo=config["repo"])

    project_id = helper.get_or_create_project(config["project_name"])
    if not project_id:
        print(f"❌ Project '{config['project_name']}' not found.")
        return
    print(f"✅ Project '{config['project_name']}' exists.")

    status_field_id = helper.get_status_field_id(project_id)

    for issue in config["issues"]:
        issue_title = issue["title"]
        issue_body = issue.get("content", "")
        issue_id = helper.create_issue(issue_title, issue_body)

        if not issue_id:
            print(f"❌ Failed to create issue '{issue_title}'")
            continue

        added = helper.add_issue_to_project(project_id, issue_id)
        if added and status_field_id:
            helper.set_issue_status(project_id, issue_id, "In Progress", status_field_id)


if __name__ == "__main__":
    main()
