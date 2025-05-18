import unittest
from unittest.mock import patch, MagicMock
import os
import sys

from src.github_prjt_automation import utils


class TestMainEdgeCases(unittest.TestCase):

    @patch("src.github_prjt_automation.utils.load_yaml", return_value={})
    @patch.dict(os.environ, {}, clear=True)
    def test_main_raises_if_no_token(self, mock_load_yaml):
        from src.github_prjt_automation.main import main
        with self.assertRaises(EnvironmentError):
            main()

#-------------------------------
@patch.dict(os.environ, {"GITHUB_TOKEN": "dummy"}, clear=True)
@patch("src.github_prjt_automation.utils.load_yaml", return_value={})
@patch("src.github_prjt_automation.utils.GitHubHelper")
def test_project_creation_failure(self, MockGitHubHelper, mock_load_yaml):
    mock_helper = MockGitHubHelper.return_value
    mock_helper.get_or_create_project.return_value = None

    from src.github_prjt_automation.main import main
    main()

    mock_helper.get_or_create_project.assert_called_once()

#-------------------------------

"""     @patch("src.github_prjt_automation.utils.load_yaml")
    @patch("src.github_prjt_automation.utils.GitHubHelper")
    def test_project_creation_failure(self, MockGitHubHelper, mock_load_yaml):
        # Simulate no project ID found
        mock_helper = MockGitHubHelper.return_value
        mock_helper.get_or_create_project.return_value = None

        mock_load_yaml.return_value = {
            "GITHUB_TOKEN": "dummy",
            "repo": "example/repo",
            "project_title": "Fake Project",
            "issues": []
        }

        from src.github_prjt_automation.main import main
        main()

        mock_helper.get_or_create_project.assert_called_once()
 """

class TestUtilsEdgeCases(unittest.TestCase):

    def setUp(self):
        self.gh = utils.GitHubHelper(token="dummy_token", repo="owner/repo")

    @patch.object(utils.GitHubHelper, "_graphql_query")
    def test_get_status_field_id_not_found(self, mock_query):
        # Simulate no status field found
        mock_query.return_value = {
            "node": {
                "fields": {
                    "nodes": [{"name": "Priority", "id": "abc123"}]  # No "Status"
                }
            }
        }

        result = self.gh.get_status_field_id("proj_id")
        self.assertEqual(result, (None, None))
        #self.assertIsNone(result)
#--------------------
    @patch.object(utils.GitHubHelper, "get_status_field_id", side_effect=Exception("API down"))
    def test_set_issue_status_failure(self, mock_status_field):
        result = self.gh.set_issue_status(123, "Todo", "field_id")
        self.assertFalse(result)
""" 
    @patch.object(utils.GitHubHelper, "_graphql_query", side_effect=Exception("API down"))
    def test_set_issue_status_failure(self, mock_query):
        result = self.gh.set_issue_status(123, "Todo", "field_id")
        self.assertFalse(result) """
# -------------------


if __name__ == "__main__":
    unittest.main()
