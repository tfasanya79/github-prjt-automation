""" | Method                  | Scenario                      |
| ----------------------- | ----------------------------- |
| `get_or_create_project` | Found & creates if missing    |
| `create_issue`          | Success and failure cases     |
| `add_issue_to_project`  | Successful add                |
| `set_issue_status`      | Field status successfully set |
| `get_status_field_id`   | Correct field & option IDs   """  


import unittest
from unittest.mock import patch, MagicMock
from github_prjt_automation.utils import GitHubHelper

class TestGitHubHelper(unittest.TestCase):

    def setUp(self):
        self.helper = GitHubHelper(token="fake-token", repo="owner/repo")
        self.helper.headers = {"Authorization": "Bearer fake-token"}

    @patch("github_prjt_automation.utils.requests.post")
    @patch("github_prjt_automation.utils.requests.get")
    def test_get_or_create_project_found(self, mock_get, mock_post):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "data": {
                "repository": {
                    "projectsV2": {
                        "nodes": [{"id": "existing_project_id"}]
                    }
                }
            }
        }

        project_id = self.helper.get_or_create_project("Existing Project")
        self.assertEqual(project_id, "existing_project_id")
        mock_post.assert_not_called()

    @patch("github_prjt_automation.utils.requests.post")
    @patch("github_prjt_automation.utils.requests.get")
    def test_get_or_create_project_creates_new(self, mock_get, mock_post):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "data": {"repository": {"projectsV2": {"nodes": []}}}
        }

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "data": {
                "createProjectV2": {"projectV2": {"id": "new_project_id"}}
            }
        }

        project_id = self.helper.get_or_create_project("New Project")
        self.assertEqual(project_id, "new_project_id")

    @patch("github_prjt_automation.utils.requests.post")
    def test_create_issue_success(self, mock_post):
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {
            "id": "issue123",
            "number": 5
        }

        issue = self.helper.create_issue("Test Issue")
        self.assertEqual(issue["id"], "issue123")

    @patch("github_prjt_automation.utils.requests.post")
    def test_create_issue_failure(self, mock_post):
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = "Bad Request"

        issue = self.helper.create_issue("Fail Issue")
        self.assertIsNone(issue)

    @patch("github_prjt_automation.utils.requests.post")
    def test_add_issue_to_project_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "data": {"addProjectV2ItemById": {"item": {"id": "item_id"}}}
        }

        item_id = self.helper.add_issue_to_project("project123", "issue123")
        self.assertEqual(item_id, "item_id")

    @patch("github_prjt_automation.utils.requests.post")
    def test_set_issue_status_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "data": {"updateProjectV2ItemFieldValue": {"projectV2Item": {"id": "updated_id"}}}
        }

        result = self.helper.set_issue_status("proj_id", 1, "Todo")
        self.assertEqual(result, "updated_id")

    @patch("github_prjt_automation.utils.requests.get")
    def test_get_status_field_id_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "data": {
                "node": {
                    "fields": {
                        "nodes": [
                            {
                                "name": "Status",
                                "id": "field123",
                                "options": [{"name": "Todo", "id": "todo123"}]
                            }
                        ]
                    }
                }
            }
        }

        field_id, option_id = self.helper.get_status_field_id("project123", "Todo")
        self.assertEqual(field_id, "field123")
        self.assertEqual(option_id, "todo123")

if __name__ == '__main__':
    unittest.main()
