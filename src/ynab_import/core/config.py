"""Configuration management for ynab-import application."""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import tomli
import tomli_w
from platformdirs import user_config_dir

from ynab_import.core.preset import Preset

logger = logging.getLogger(__name__)

DEFAULT_EXPORT_PATH = str(Path.home() / "Downloads" / "ynab-exports")


@dataclass
class Config:
    """Configuration data for ynab-import application."""

    active_preset: str | None = None
    export_path: str = field(default_factory=lambda: DEFAULT_EXPORT_PATH)

    def to_dict(self) -> dict[str, Any]:
        """Convert Config to dictionary for TOML serialization."""
        data = {}
        # Only include active_preset if it's not None (TOML doesn't support None)
        if self.active_preset is not None:
            data["active_preset"] = self.active_preset
        data["export_path"] = self.export_path
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        """Create Config from dictionary loaded from TOML."""
        return cls(
            active_preset=data.get("active_preset"),
            export_path=data.get("export_path", DEFAULT_EXPORT_PATH),
        )


def get_config_dir() -> Path:
    """Get the configuration directory path."""
    return Path(user_config_dir("ynab-import"))


def get_config_file_path() -> Path:
    """Get the full path to the configuration file."""
    return get_config_dir() / "config.toml"


def ensure_config_exists() -> Config:
    """Ensure configuration file exists and load it."""
    config_path = get_config_file_path()
    config_dir = config_path.parent

    # Create config directory if it doesn't exist
    if not config_dir.exists():
        logger.info(f"Creating configuration directory: {config_dir}")
        try:
            config_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.error(f"Failed to create config directory {config_dir}: {e}")
            raise PermissionError(
                f"Cannot create config directory: {config_dir}"
            ) from e

    # Create config file if it doesn't exist
    if not config_path.exists():
        logger.info(f"Creating default configuration file: {config_path}")
        default_config = Config()
        try:
            _save_config_to_file(config_path, default_config)
        except OSError as e:
            logger.error(f"Failed to create config file {config_path}: {e}")
            raise PermissionError(f"Cannot create config file: {config_path}") from e
        return default_config

    # Load existing config
    logger.debug(f"Loading configuration from: {config_path}")
    return load_config()


def load_config() -> Config:
    """Load configuration from the TOML file."""
    config_path = get_config_file_path()

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with open(config_path, "rb") as file:
            toml_data = tomli.load(file)
        logger.debug(f"Successfully loaded config from {config_path}")
        return Config.from_dict(toml_data)
    except tomli.TOMLDecodeError as e:
        logger.error(f"Invalid TOML in config file {config_path}: {e}")
        raise
    except OSError as e:
        logger.error(f"Error reading config file {config_path}: {e}")
        raise


def update_config_value(key: str, value: Any) -> Config:
    """Update a single configuration value and save to file."""
    # Load current config
    config = ensure_config_exists()

    # Update the specified value
    if key == "active_preset":
        if value is not None and not isinstance(value, str):
            raise ValueError("active_preset must be a string or None")
        config.active_preset = value
    elif key == "export_path":
        if not isinstance(value, str | Path):
            raise ValueError("export_path must be a string or Path")
        config.export_path = str(value)
    else:
        raise ValueError(f"Unknown configuration key: {key}")

    # Save updated config
    save_config(config)
    logger.info(f"Updated configuration: {key} = {value}")
    return config


def save_config(config: Config) -> None:
    """Save configuration to the TOML file."""
    config_path = get_config_file_path()
    _save_config_to_file(config_path, config)


def _save_config_to_file(config_path: Path, config: Config) -> None:
    """Internal function to save config to a specific file path."""
    try:
        with open(config_path, "wb") as file:
            tomli_w.dump(config.to_dict(), file)
        logger.debug(f"Configuration saved to {config_path}")
    except OSError as e:
        logger.error(f"Failed to save config to {config_path}: {e}")
        raise PermissionError(f"Cannot write to config file: {config_path}") from e


def get_presets_dir() -> Path:
    """Get the presets directory path."""
    return get_config_dir() / "presets"


def get_presets_file_path() -> Path:
    """Get the full path to the presets file."""
    return get_presets_dir() / "presets.json"


def ensure_presets_dir_exists() -> None:
    """Ensure the presets directory exists."""
    presets_dir = get_presets_dir()
    if not presets_dir.exists():
        logger.info(f"Creating presets directory: {presets_dir}")
        try:
            presets_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.error(f"Failed to create presets directory {presets_dir}: {e}")
            raise PermissionError(
                f"Cannot create presets directory: {presets_dir}"
            ) from e


def load_presets() -> dict[str, "Preset"]:
    """Load all presets from the presets file."""
    from ynab_import.file_rw.readers import read_presets_file

    presets_path = get_presets_file_path()
    if not presets_path.exists():
        return {}

    try:
        return read_presets_file(presets_path)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading presets from {presets_path}: {e}")
        return {}


def save_preset(preset_key: str, preset: "Preset") -> None:
    """Save a single preset to the presets file."""
    from ynab_import.file_rw.writers import write_presets_json

    ensure_presets_dir_exists()

    # Load existing presets
    presets = load_presets()

    # Add/update the preset
    presets[preset_key] = preset

    # Save all presets
    presets_path = get_presets_file_path()
    write_presets_json(presets_path, presets)
    logger.info(f"Saved preset '{preset_key}' to {presets_path}")


def delete_preset(preset_key: str) -> bool:
    """Delete a preset from the presets file."""
    from ynab_import.file_rw.writers import write_presets_json

    presets = load_presets()

    if preset_key not in presets:
        return False

    del presets[preset_key]

    # Save updated presets
    if presets:  # Only write if there are remaining presets
        presets_path = get_presets_file_path()
        write_presets_json(presets_path, presets)
    else:
        # Remove the file if no presets remain
        presets_path = get_presets_file_path()
        if presets_path.exists():
            presets_path.unlink()

    logger.info(f"Deleted preset '{preset_key}'")
    return True
