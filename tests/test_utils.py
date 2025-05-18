import pytest
from unittest.mock import patch, MagicMock
from src.github_prjt_automation.utils import GitHubHelper


@pytest.fixture
def github_helper():
    return GitHubHelper(token="fake-token", repo="owner/repo")


@patch("requests.post")
def test_create_issue_success(mock_post, github_helper):
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"title": "Test Issue"}
    mock_post.return_value = mock_response

    issue = github_helper.create_issue("Test Issue")
    assert issue["title"] == "Test Issue"


@patch("requests.post")
def test_create_issue_failure(mock_post, github_helper):
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.text = "Forbidden"
    mock_post.return_value = mock_response

    result = github_helper.create_issue("Blocked Issue")
    assert result is None


@patch("requests.post")
def test_set_issue_status_handles_missing_ids(mock_post, github_helper):
    # Patch both internal methods used by set_issue_status
    github_helper.get_status_field_id = MagicMock(return_value=(None, None))
    github_helper._get_project_item_id = MagicMock(return_value="some-id")

    result = github_helper.set_issue_status(123, "In Progress", "proj-id")
    assert not result  # Should fail due to missing field ID


@patch("requests.post")
def test_get_or_create_project_returns_existing(mock_post, github_helper):
    # Simulate GraphQL query returning an existing project
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "data": {
            "viewer": {
                "projectsV2": {
                    "nodes": [{"title": "My Project", "id": "proj-123"}]
                }
            }
        }
    }

    project_id = github_helper.get_or_create_project("My Project")
    assert project_id == "proj-123"
