import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import subprocess
from unittest.mock import patch

import pytest

from ynab_import import __version__, get_version


class TestVersion:
    """Tests for version functionality."""

    @pytest.mark.unit
    def test_get_version_returns_string(self) -> None:
        """Test that get_version returns a string."""
        version = get_version()
        assert isinstance(version, str)
        assert len(version) > 0

    @pytest.mark.unit
    def test_version_matches_package_version(self) -> None:
        """Test that __version__ matches get_version()."""
        assert __version__ == get_version()

    @pytest.mark.unit
    def test_version_format(self) -> None:
        """Test that version follows semantic versioning pattern."""
        version = get_version()
        # Should match pattern like "0.5.0" or "1.2.3"
        parts = version.split(".")
        assert len(parts) >= 2, f"Version should have at least 2 parts: {version}"

        for part in parts:
            assert part.isdigit(), f"Version parts should be numeric: {version}"

    @pytest.mark.integration
    def test_cli_version_flag_long(self) -> None:
        """Test that --version flag works in CLI."""
        result = subprocess.run(
            ["uv", "run", "ynab-converter", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "ynab-converter" in result.stdout
        assert get_version() in result.stdout

    @pytest.mark.integration
    def test_cli_version_flag_short(self) -> None:
        """Test that -v flag works in CLI."""
        result = subprocess.run(
            ["uv", "run", "ynab-converter", "-v"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "ynab-converter" in result.stdout
        assert get_version() in result.stdout

    @pytest.mark.unit
    def test_version_fallback_on_exception(self) -> None:
        """Test that version falls back gracefully when metadata unavailable."""
        with patch("ynab_import.version", side_effect=Exception("Mock error")):
            # Re-import to trigger the exception handling
            import importlib

            import ynab_import

            importlib.reload(ynab_import)

            # Should fall back to pyproject.toml version or "unknown"
            fallback_version = ynab_import.get_version()
            assert isinstance(fallback_version, str)
            assert fallback_version != ""
            # Should either be a valid version or "unknown"
            assert (
                fallback_version == "unknown" or len(fallback_version.split(".")) >= 2
            )
