import unittest
from unittest.mock import MagicMock, Mock, mock_open, patch

from agent.models import ToolResult
from agent.tools import DirectoryListTool, FileEditTool, FileReadTool


class TestFileTools(unittest.TestCase):
    def setUp(self):
        self.read_tool = FileReadTool()
        self.list_tool = DirectoryListTool()
        self.edit_tool = FileEditTool()

    @patch("builtins.open", new_callable=mock_open, read_data="test file content")
    @patch("agent.tools.agent_tools._check_project_path")
    def test_read_file_success(self, mock_check, mock_file):
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.name = "test.txt"
        mock_check.return_value = mock_path

        result = self.read_tool.execute(path="test.txt")

        self.assertTrue(result.ok)
        self.assertEqual(result.data, "test file content")

    @patch("agent.tools.agent_tools._check_project_path")
    def test_read_file_access_denied(self, mock_check):
        mock_check.return_value = ToolResult(ok=False, error="Access denied")

        result = self.read_tool.execute(path="../etc/passwd")

        self.assertFalse(result.ok)
        self.assertIn("Access denied", result.error)

    @patch("agent.tools.agent_tools._check_project_path")
    def test_list_directory_success(self, mock_check):
        mock_dir = MagicMock()
        mock_dir.is_dir.return_value = True

        # Mock directory items - need to be sortable
        mock_item1 = MagicMock()
        mock_item1.is_file.return_value = True
        mock_item1.name = "file1.txt"
        mock_item1.__lt__ = lambda self, other: self.name < other.name

        mock_item2 = MagicMock()
        mock_item2.is_file.return_value = False
        mock_item2.name = "subdir"
        mock_item2.__lt__ = lambda self, other: self.name < other.name

        mock_item3 = MagicMock()
        mock_item3.is_file.return_value = True
        mock_item3.name = "file2.py"
        mock_item3.__lt__ = lambda self, other: self.name < other.name

        mock_dir.iterdir.return_value = [mock_item1, mock_item2, mock_item3]
        mock_check.return_value = mock_dir

        result = self.list_tool.execute(".")

        self.assertTrue(result.ok)
        self.assertIn("FILE: file1.txt", result.data["items"])
        self.assertIn("DIR:  subdir", result.data["items"])
        self.assertIn("FILE: file2.py", result.data["items"])

    @patch("builtins.open", new_callable=mock_open, read_data="old content")
    @patch("agent.tools.agent_tools._check_project_path")
    def test_edit_file_success(self, mock_check, mock_file):
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_check.return_value = mock_path

        result = self.edit_tool.execute("test.txt", "old content", "new content")

        self.assertTrue(result.ok)
        mock_file().write.assert_called_with("new content")

    @patch("builtins.open", new_callable=mock_open, read_data="different content")
    @patch("agent.tools.agent_tools._check_project_path")
    def test_edit_file_text_not_found(self, mock_check, mock_file):
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_check.return_value = mock_path

        result = self.edit_tool.execute("test.txt", "old content", "new content")

        self.assertFalse(result.ok)
        self.assertIn("Text not found", result.error)


class TestToolSchemas(unittest.TestCase):
    def test_read_tool_schema(self):
        tool = FileReadTool()
        schema = tool.get_schema()

        self.assertEqual(schema["name"], "read_file")
        self.assertIn("path", schema["parameters"]["required"])
        self.assertEqual(
            schema["parameters"]["properties"]["max_lines"]["default"], 2000
        )

    def test_list_tool_schema(self):
        tool = DirectoryListTool()
        schema = tool.get_schema()

        self.assertEqual(schema["name"], "list_dir")
        self.assertEqual(schema["parameters"]["properties"]["path"]["default"], ".")

    def test_edit_tool_schema(self):
        tool = FileEditTool()
        schema = tool.get_schema()

        self.assertEqual(schema["name"], "edit_file")
        required = schema["parameters"]["required"]
        self.assertIn("path", required)
        self.assertIn("old_str", required)
        self.assertIn("new_str", required)


if __name__ == "__main__":
    unittest.main()
