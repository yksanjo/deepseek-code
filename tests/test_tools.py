"""Tests for the tool system."""

import os
import tempfile
from pathlib import Path

import pytest

from deepseek_code.tools.base import ToolRegistry, ToolResult
from deepseek_code.tools.file_tools import ReadFileTool, WriteFileTool, EditFileTool
from deepseek_code.tools.search_tools import GlobTool, GrepTool


class TestToolRegistry:
    """Test cases for ToolRegistry."""

    def test_register_and_get_tool(self):
        """Tools should be retrievable after registration."""
        registry = ToolRegistry()
        tool = ReadFileTool()
        registry.register(tool)
        
        retrieved = registry.get(tool.name)
        assert retrieved is not None
        assert retrieved.name == tool.name

    def test_get_nonexistent_tool(self):
        """Getting a nonexistent tool should return None."""
        registry = ToolRegistry()
        result = registry.get("nonexistent_tool")
        assert result is None

    def test_list_tools(self):
        """All registered tools should be listable."""
        registry = ToolRegistry()
        tools = registry.list_tools()
        assert len(tools) > 0


class TestReadFileTool:
    """Test cases for ReadFileTool."""

    def test_read_file_success(self):
        """Should successfully read a file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def hello():\n    print('hello')")
            temp_path = f.name

        try:
            tool = ReadFileTool()
            result = tool.execute(path=temp_path)
            
            assert result.success is True
            assert "def hello" in result.output
        finally:
            os.unlink(temp_path)

    def test_read_file_not_found(self):
        """Should handle file not found gracefully."""
        tool = ReadFileTool()
        result = tool.execute(path="/nonexistent/file.py")
        
        assert result.success is False
        assert "not found" in result.output.lower() or "error" in result.output.lower()


class TestWriteFileTool:
    """Test cases for WriteFileTool."""

    def test_write_file_success(self):
        """Should successfully write to a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.py")
            
            tool = WriteFileTool()
            result = tool.execute(path=file_path, content="print('hello')")
            
            assert result.success is True
            assert os.path.exists(file_path)
            
            with open(file_path) as f:
                assert f.read() == "print('hello')"

    def test_write_file_overwrite(self):
        """Should overwrite existing files when specified."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("old content")
            temp_path = f.name

        try:
            tool = WriteFileTool()
            result = tool.execute(path=temp_path, content="new content")
            
            assert result.success is True
            with open(temp_path) as f:
                assert f.read() == "new content"
        finally:
            os.unlink(temp_path)


class TestEditFileTool:
    """Test cases for EditFileTool."""

    def test_edit_file_success(self):
        """Should successfully edit a file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def hello():\n    print('hello')")
            temp_path = f.name

        try:
            tool = EditFileTool()
            result = tool.execute(
                path=temp_path,
                old="print('hello')",
                new="print('world')"
            )
            
            assert result.success is True
            with open(temp_path) as f:
                content = f.read()
                assert "print('world')" in content
                assert "print('hello')" not in content
        finally:
            os.unlink(temp_path)

    def test_edit_file_no_match(self):
        """Should handle when old string is not found."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def hello():\n    print('hello')")
            temp_path = f.name

        try:
            tool = EditFileTool()
            result = tool.execute(
                path=temp_path,
                old="not found",
                new="something else"
            )
            
            assert result.success is False
        finally:
            os.unlink(temp_path)


class TestGlobTool:
    """Test cases for GlobTool."""

    def test_glob_python_files(self):
        """Should find Python files in directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            Path(tmpdir, "test1.py").touch()
            Path(tmpdir, "test2.py").touch()
            Path(tmpdir, "readme.txt").touch()
            
            tool = GlobTool()
            result = tool.execute(path=tmpdir, pattern="*.py")
            
            assert result.success is True
            assert "test1.py" in result.output
            assert "test2.py" in result.output
            assert "readme.txt" not in result.output

    def test_glob_recursive(self):
        """Should find files recursively."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested structure
            Path(tmpdir, "root.py").touch()
            subdir = Path(tmpdir, "subdir")
            subdir.mkdir()
            Path(subdir, "nested.py").touch()
            
            tool = GlobTool()
            result = tool.execute(path=tmpdir, pattern="**/*.py")
            
            assert result.success is True
            assert "root.py" in result.output
            assert "nested.py" in result.output


class TestGrepTool:
    """Test cases for GrepTool."""

    def test_grep_finds_matches(self):
        """Should find matching patterns in files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            test_file = Path(tmpdir, "test.py")
            test_file.write_text("def hello():\n    return 'hello'\n\ndef world():\n    return 'world'")
            
            tool = GrepTool()
            result = tool.execute(pattern="def ", path=tmpdir)
            
            assert result.success is True
            assert "hello" in result.output
            assert "world" in result.output

    def test_grep_no_matches(self):
        """Should handle no matches gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "test.py")
            test_file.write_text("print('hello')")
            
            tool = GrepTool()
            result = tool.execute(pattern="def ", path=tmpdir)
            
            assert result.success is True
            # Should indicate no matches found
