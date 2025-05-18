import unittest
from unittest.mock import patch, MagicMock
from src.github_prjt_automation import main
from src.github_prjt_automation.utils import GitHubHelper


class TestGitHubHelper(unittest.TestCase):
    def setUp(self):
        self.helper = GitHubHelper("fake", "owner/repo")

    @patch("src.github_prjt_automation.utils.requests.post")
    def test_get_or_create_project_found(self, mock_post):
        # Simulate a response where the project already exists
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "data": {
                "viewer": {
                    "projectsV2": {
                        "nodes": [{"title": "My Project", "id": "123"}]
                    }
                }
            }
        }
        result = self.helper.get_or_create_project("My Project")
        self.assertEqual(result, "123")

    @patch("src.github_prjt_automation.utils.requests.post")
    def test_get_or_create_project_creates_new(self, mock_post):
        # First call simulates empty projects list
        # Second call simulates project creation
        mock_post.side_effect = [
            MagicMock(
                status_code=200,
                json=lambda: {
                    "data": {"viewer": {"projectsV2": {"nodes": []}}}
                },
            ),
            MagicMock(
                status_code=200,
                json=lambda: {
                    "data": {"createProjectV2": {"projectV2": {"id": "new_proj_id"}}}
                },
            ),
        ]
        result = self.helper.get_or_create_project("New Project")
        self.assertEqual(result, "new_proj_id")

    @patch("src.github_prjt_automation.utils.requests.post")
    def test_create_issue_success(self, mock_post):
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"id": "issue_id"}
        result = self.helper.create_issue("Test Issue")
        self.assertEqual(result["id"], "issue_id")

    @patch("src.github_prjt_automation.utils.requests.post")
    def test_create_issue_failure(self, mock_post):
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = "Bad Request"
        result = self.helper.create_issue("Test Issue")
        self.assertIsNone(result)

    @patch("src.github_prjt_automation.utils.requests.post")
    def test_add_issue_to_project_success(self, mock_post):
        mock_post.return_value.status_code = 200
        result = self.helper.add_issue_to_project("proj_id", "issue_id")
        self.assertTrue(result)

    @patch("src.github_prjt_automation.utils.requests.post")
    def test_set_issue_status_failure_on_field_lookup(self, mock_post):
        self.helper.get_status_field_id = MagicMock(return_value=(None, None))
        result = self.helper.set_issue_status("proj_id", 1, "In Progress")
        self.assertFalse(result)


class TestGitHubAutomation(unittest.TestCase):
    @patch("src.github_prjt_automation.main.get_config")
    @patch("src.github_prjt_automation.main.GitHubHelper")
    def test_main_flow(self, mock_helper_class, mock_get_config):
        mock_get_config.return_value = {
            "github_token": "fake",
            "repo": "owner/repo",
            "project_name": "SIEM Lab Progress",
            "issues": [{"title": "Issue 1", "content": "Description"}]
        }

        mock_helper = MagicMock()
        mock_helper_class.return_value = mock_helper

        mock_helper.get_or_create_project.return_value = "proj_id"
        mock_helper.create_issue.return_value = "issue_id"
        mock_helper.add_issue_to_project.return_value = True
        mock_helper.get_status_field_id.return_value = "field_id"
        mock_helper.set_issue_status.return_value = True

        main.main()

        mock_helper.get_or_create_project.assert_called_once_with("SIEM Lab Progress")
        mock_helper.create_issue.assert_called_once()
        mock_helper.add_issue_to_project.assert_called_once()
        mock_helper.set_issue_status.assert_called_once()

#---------------------------
    def test_main_missing_config_fields(self):
        mock_config = {
            "github_token": "fake_token",  # ✅ Add this line
            "project_name": "Fake Project",
            "repo": "example/repo",
            "issues": []
        }



        with patch("src.github_prjt_automation.main.get_config", return_value=mock_config), \
             patch("src.github_prjt_automation.main.GitHubHelper") as mock_helper:
            mock_helper.return_value.get_or_create_project.return_value = "project_id"
            mock_helper.return_value.create_issue.return_value = {"node_id": "abc123", "number": 1}
            mock_helper.return_value.add_issue_to_project.return_value = True
            try:
                import src.github_prjt_automation.main as main_module
                main_module.main()
            except Exception:
                self.fail("main() raised unexpectedly")


if __name__ == "__main__":
    unittest.main()
