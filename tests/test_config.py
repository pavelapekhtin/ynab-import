import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import tempfile
from unittest.mock import patch

import pytest
import tomli

from ynab_import.core.config import (
    Config,
    ensure_config_exists,
    get_config_dir,
    get_config_file_path,
    load_config,
    save_config,
    update_config_value,
)


class TestConfig:
    """Tests for Config dataclass."""

    @pytest.mark.unit
    def test_config_default_values(self) -> None:
        """Test Config dataclass with default values."""
        # Act
        config = Config()

        # Assert
        assert config.active_preset is None
        expected_path = str(Path.home() / "Downloads" / "ynab-exports")
        assert config.export_path == expected_path

    @pytest.mark.unit
    def test_config_with_custom_values(self) -> None:
        """Test Config dataclass with custom values."""
        # Arrange
        active_preset = "bulder_bank"
        export_path = "/custom/export/path"

        # Act
        config = Config(active_preset=active_preset, export_path=export_path)

        # Assert
        assert config.active_preset == active_preset
        assert config.export_path == export_path

    @pytest.mark.unit
    def test_config_to_dict(self) -> None:
        """Test Config to_dict method."""
        # Arrange
        config = Config(active_preset="test_preset", export_path="/test/path")

        # Act
        result = config.to_dict()

        # Assert
        expected = {
            "active_preset": "test_preset",
            "export_path": "/test/path",
        }
        assert result == expected

    @pytest.mark.unit
    def test_config_from_dict_complete(self) -> None:
        """Test Config from_dict with all values present."""
        # Arrange
        data = {
            "active_preset": "eurocard",
            "export_path": "/custom/exports",
        }

        # Act
        config = Config.from_dict(data)

        # Assert
        assert config.active_preset == "eurocard"
        assert config.export_path == "/custom/exports"

    @pytest.mark.unit
    def test_config_from_dict_partial(self) -> None:
        """Test Config from_dict with missing values (uses defaults)."""
        # Arrange
        data = {"active_preset": "test_preset"}

        # Act
        config = Config.from_dict(data)

        # Assert
        assert config.active_preset == "test_preset"
        expected_path = str(Path.home() / "Downloads" / "ynab-exports")
        assert config.export_path == expected_path

    @pytest.mark.unit
    def test_config_from_dict_empty(self) -> None:
        """Test Config from_dict with empty dictionary."""
        # Arrange
        data = {}

        # Act
        config = Config.from_dict(data)

        # Assert
        assert config.active_preset is None
        expected_path = str(Path.home() / "Downloads" / "ynab-exports")
        assert config.export_path == expected_path


class TestConfigPaths:
    """Tests for configuration path functions."""

    @patch("ynab_import.core.config.user_config_dir")
    @pytest.mark.unit
    def test_get_config_dir(self, mock_user_config_dir) -> None:
        """Test get_config_dir function."""
        # Arrange
        mock_user_config_dir.return_value = "/home/user/.config/ynab-converter"

        # Act
        result = get_config_dir()

        # Assert
        mock_user_config_dir.assert_called_once_with("ynab-converter")
        assert result == Path("/home/user/.config/ynab-converter")

    @patch("ynab_import.core.config.get_config_dir")
    @pytest.mark.unit
    def test_get_config_file_path(self, mock_get_config_dir) -> None:
        """Test get_config_file_path function."""
        # Arrange
        mock_get_config_dir.return_value = Path("/test/config/dir")

        # Act
        result = get_config_file_path()

        # Assert
        assert result == Path("/test/config/dir/config.toml")


class TestEnsureConfigExists:
    """Tests for ensure_config_exists function."""

    @pytest.mark.unit
    def test_ensure_config_exists_creates_new(self) -> None:
        """Test ensure_config_exists creates new config when none exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "ynab-converter"
            config_file = config_dir / "config.toml"

            with patch(
                "ynab_import.core.config.get_config_dir", return_value=config_dir
            ):
                # Act
                config = ensure_config_exists()

                # Assert
                assert config_dir.exists()
                assert config_file.exists()
                assert config.active_preset is None
                expected_path = str(Path.home() / "Downloads" / "ynab-exports")
                assert config.export_path == expected_path

                # Verify file content
                with open(config_file, "rb") as f:
                    toml_data = tomli.load(f)
                assert (
                    "active_preset" not in toml_data
                )  # None values are not serialized
                assert toml_data["export_path"] == expected_path

    @pytest.mark.unit
    def test_ensure_config_exists_loads_existing(self) -> None:
        """Test ensure_config_exists loads existing config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "ynab-converter"

            # Create existing config
            config_dir.mkdir(parents=True)
            existing_config = Config(
                active_preset="existing_preset", export_path="/existing/path"
            )

            with patch(
                "ynab_import.core.config.get_config_dir", return_value=config_dir
            ):
                save_config(existing_config)

                # Act
                loaded_config = ensure_config_exists()

                # Assert
                assert loaded_config.active_preset == "existing_preset"
                assert loaded_config.export_path == "/existing/path"

    @pytest.mark.unit
    def test_ensure_config_exists_permission_error(self) -> None:
        """Test ensure_config_exists handles permission errors (Unix/Linux/macOS only)."""
        with patch("ynab_import.core.config.get_config_dir") as mock_get_dir:
            # Mock a path that would cause permission error on Unix systems
            mock_get_dir.return_value = Path("/root/forbidden")

            # Act & Assert
            with pytest.raises(PermissionError):
                ensure_config_exists()


class TestLoadConfig:
    """Tests for load_config function."""

    @pytest.mark.unit
    def test_load_config_success(self) -> None:
        """Test successful config loading."""
        with tempfile.NamedTemporaryFile(
            mode="wb", suffix=".toml", delete=False
        ) as temp_file:
            config_path = Path(temp_file.name)

            # Create test config content
            import tomli_w

            test_data = {"active_preset": "test_preset", "export_path": "/test/exports"}
            tomli_w.dump(test_data, temp_file)

        try:
            with patch(
                "ynab_import.core.config.get_config_file_path", return_value=config_path
            ):
                # Act
                config = load_config()

                # Assert
                assert config.active_preset == "test_preset"
                assert config.export_path == "/test/exports"
        finally:
            config_path.unlink()

    @pytest.mark.unit
    def test_load_config_file_not_found(self) -> None:
        """Test load_config raises FileNotFoundError when file doesn't exist."""
        nonexistent_path = Path("/nonexistent/config.toml")

        with patch(
            "ynab_import.core.config.get_config_file_path",
            return_value=nonexistent_path,
        ):
            # Act & Assert
            with pytest.raises(FileNotFoundError, match="Configuration file not found"):
                load_config()

    @pytest.mark.unit
    def test_load_config_invalid_toml(self) -> None:
        """Test load_config handles invalid TOML gracefully."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False
        ) as temp_file:
            config_path = Path(temp_file.name)
            temp_file.write("invalid toml content [[[")

        try:
            with patch(
                "ynab_import.core.config.get_config_file_path", return_value=config_path
            ):
                # Act & Assert
                with pytest.raises(tomli.TOMLDecodeError):
                    load_config()
        finally:
            config_path.unlink()


class TestUpdateConfigValue:
    """Tests for update_config_value function."""

    @pytest.fixture
    def mock_config_setup(self):
        """Setup mock config environment."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "ynab-converter"
            config_dir.mkdir(parents=True)

            # Create initial config
            initial_config = Config()
            with patch(
                "ynab_import.core.config.get_config_dir", return_value=config_dir
            ):
                save_config(initial_config)
                yield config_dir

    @pytest.mark.unit
    def test_update_config_active_preset(self, mock_config_setup) -> None:
        """Test updating active_preset configuration."""
        config_dir = mock_config_setup

        with patch("ynab_import.core.config.get_config_dir", return_value=config_dir):
            # Act
            updated_config = update_config_value("active_preset", "new_preset")

            # Assert
            assert updated_config.active_preset == "new_preset"

            # Verify persistence
            loaded_config = load_config()
            assert loaded_config.active_preset == "new_preset"

    @pytest.mark.unit
    def test_update_config_active_preset_to_none(self, mock_config_setup) -> None:
        """Test setting active_preset to None."""
        config_dir = mock_config_setup

        with patch("ynab_import.core.config.get_config_dir", return_value=config_dir):
            # Act
            updated_config = update_config_value("active_preset", None)

            # Assert
            assert updated_config.active_preset is None

    @pytest.mark.unit
    def test_update_config_export_path(self, mock_config_setup) -> None:
        """Test updating export_path configuration."""
        config_dir = mock_config_setup
        new_path = "/new/export/path"

        with patch("ynab_import.core.config.get_config_dir", return_value=config_dir):
            # Act
            updated_config = update_config_value("export_path", new_path)

            # Assert
            assert updated_config.export_path == new_path

            # Verify persistence
            loaded_config = load_config()
            assert loaded_config.export_path == new_path

    @pytest.mark.unit
    def test_update_config_export_path_with_path_object(
        self, mock_config_setup
    ) -> None:
        """Test updating export_path with Path object."""
        config_dir = mock_config_setup
        new_path = Path("/path/object/export")

        with patch("ynab_import.core.config.get_config_dir", return_value=config_dir):
            # Act
            updated_config = update_config_value("export_path", new_path)

            # Assert
            assert updated_config.export_path == str(new_path)

    @pytest.mark.unit
    def test_update_config_invalid_key(self, mock_config_setup) -> None:
        """Test updating with invalid configuration key."""
        config_dir = mock_config_setup

        with patch("ynab_import.core.config.get_config_dir", return_value=config_dir):
            # Act & Assert
            with pytest.raises(
                ValueError, match="Unknown configuration key: invalid_key"
            ):
                update_config_value("invalid_key", "some_value")

    @pytest.mark.unit
    def test_update_config_invalid_preset_type(self, mock_config_setup) -> None:
        """Test updating active_preset with invalid type."""
        config_dir = mock_config_setup

        with patch("ynab_import.core.config.get_config_dir", return_value=config_dir):
            # Act & Assert
            with pytest.raises(
                ValueError, match="active_preset must be a string or None"
            ):
                update_config_value("active_preset", 123)

    @pytest.mark.unit
    def test_update_config_invalid_path_type(self, mock_config_setup) -> None:
        """Test updating export_path with invalid type."""
        config_dir = mock_config_setup

        with patch("ynab_import.core.config.get_config_dir", return_value=config_dir):
            # Act & Assert
            with pytest.raises(
                ValueError, match="export_path must be a string or Path"
            ):
                update_config_value("export_path", 123)


class TestSaveConfig:
    """Tests for save_config function."""

    @pytest.mark.unit
    def test_save_config_success(self) -> None:
        """Test successful config saving."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "ynab-converter"
            config_file = config_dir / "config.toml"
            config_dir.mkdir(parents=True)

            config = Config(active_preset="test_save", export_path="/save/test")

            with patch(
                "ynab_import.core.config.get_config_dir", return_value=config_dir
            ):
                # Act
                save_config(config)

                # Assert
                assert config_file.exists()
                with open(config_file, "rb") as f:
                    saved_data = tomli.load(f)

                assert saved_data["active_preset"] == "test_save"
                assert saved_data["export_path"] == "/save/test"

    @pytest.mark.unit
    def test_save_config_permission_error(self) -> None:
        """Test save_config handles permission errors (Unix/Linux/macOS only)."""
        config = Config()
        forbidden_path = Path("/root/forbidden/config.toml")

        with patch(
            "ynab_import.core.config.get_config_file_path", return_value=forbidden_path
        ):
            # Act & Assert
            with pytest.raises(PermissionError):
                save_config(config)


class TestIntegrationScenarios:
    """Integration tests for configuration functionality."""

    @pytest.mark.integration
    def test_full_config_workflow(self) -> None:
        """Test complete configuration workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "ynab-converter"

            with patch(
                "ynab_import.core.config.get_config_dir", return_value=config_dir
            ):
                # Ensure config exists (creates default)
                config1 = ensure_config_exists()
                assert config1.active_preset is None

                # Update active preset
                config2 = update_config_value("active_preset", "test_preset")
                assert config2.active_preset == "test_preset"

                # Update export path
                config3 = update_config_value("export_path", "/custom/path")
                assert config3.export_path == "/custom/path"
                assert (
                    config3.active_preset == "test_preset"
                )  # Should retain previous value

                # Load fresh config to verify persistence
                config4 = load_config()
                assert config4.active_preset == "test_preset"
                assert config4.export_path == "/custom/path"

                # Reset active preset to None
                config5 = update_config_value("active_preset", None)
                assert config5.active_preset is None
                assert config5.export_path == "/custom/path"

    @pytest.mark.integration
    def test_concurrent_access_simulation(self) -> None:
        """Test that config handles multiple access patterns correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "ynab-converter"

            with patch(
                "ynab_import.core.config.get_config_dir", return_value=config_dir
            ):
                # Multiple ensure_config_exists calls should be safe
                config1 = ensure_config_exists()
                config2 = ensure_config_exists()

                assert config1.active_preset == config2.active_preset
                assert config1.export_path == config2.export_path

                # Update and reload multiple times
                for i in range(3):
                    update_config_value("active_preset", f"preset_{i}")
                    loaded = load_config()
                    assert loaded.active_preset == f"preset_{i}"
