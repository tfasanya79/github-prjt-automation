import unittest
from unittest.mock import patch, MagicMock
import os
from src.github_prjt_automation.utils import GitHubHelper
from src.github_prjt_automation import utils


class TestMainEdgeCases(unittest.TestCase):

    @patch("src.github_prjt_automation.main.get_config", return_value={})
    @patch.dict(os.environ, {}, clear=True)
    def test_main_raises_if_no_token(self, mock_config):
        from src.github_prjt_automation.main import main
        with self.assertRaises(EnvironmentError):
            main()

    @patch("src.github_prjt_automation.main.GitHubHelper")
    @patch("src.github_prjt_automation.main.get_config")
    def test_project_creation_failure(self, mock_get_config, MockGitHubHelper):
        mock_get_config.return_value = {
            "github_token": "fake",
            "repo": "owner/repo",
            "project_name": "Test Project",
            "issues": [{"title": "Bug", "content": "Steps to reproduce..."}]
        }

        mock_helper = MockGitHubHelper.return_value
        mock_helper.get_or_create_project.side_effect = Exception("API down")

        from src.github_prjt_automation.main import main
        with self.assertRaises(Exception):
            main()

        mock_helper.get_or_create_project.assert_called_once()


class TestUtilsEdgeCases(unittest.TestCase):

    def setUp(self):
        self.gh = utils.GitHubHelper(token="dummy_token", repo="owner/repo")

    @patch.object(utils.GitHubHelper, "_graphql_query")
    def test_get_status_field_id_not_found(self, mock_query):
        mock_query.return_value = {
            "node": {
                "fields": {
                    "nodes": [{"name": "Priority", "id": "abc123"}]  # No "Status"
                }
            }
        }

        result = self.gh.get_status_field_id("proj_id")
        self.assertEqual(result, (None, None))

    @patch.object(utils.GitHubHelper, "get_status_field_id", side_effect=Exception("API down"))
    def test_set_issue_status_failure(self, mock_status_field):
        result = self.gh.set_issue_status(123, "Todo", "field_id")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
