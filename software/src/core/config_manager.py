#!/usr/bin/env python3
# AGP Power Monitor
# Copyright (C) 2025 - tehsiggi

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import yaml
import os
from typing import Any, Dict, List, Callable


class ConfigManager:
    """
    Manages configuration settings from config.yaml and command line arguments.
    Provides a centralized way to access and modify settings.
    
    Config values precedence:
    1. Command line arguments (highest priority)
    2. Config file values
    3. Default values (lowest priority)
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the ConfigManager.
        
        Args:
            config_path: Path to the config.yaml file (None for default path)
        """
        self.config_data = {}
        self.command_line_overrides = {}
        self.callbacks = {}
        
        # Default config path is in the root software directory
        if config_path is None:
            # Get the path of the directory containing this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Navigate up to the software directory
            software_dir = os.path.abspath(os.path.join(current_dir, "../.."))
            config_path = os.path.join(software_dir, "config.yaml")
            
        self.config_path = config_path
        
        # Load the config file
        self.load_config()
    
    def load_config(self) -> bool:
        """
        Load configuration from the YAML file.
        
        Returns:
            True if loading was successful, False otherwise
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config_data = yaml.safe_load(f) or {}
                return True
            else:
                print(f"Warning: Config file not found at {self.config_path}")
                self.config_data = {}
                return False
        except Exception as e:
            print(f"Error loading config file: {e}")
            self.config_data = {}
            return False
    
    def save_config(self) -> bool:
        """
        Save current configuration to the YAML file.
        
        Returns:
            True if saving was successful, False otherwise
        """
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config_data, f, default_flow_style=False)
            return True
        except Exception as e:
            print(f"Error saving config file: {e}")
            return False
    
    def set_command_line_override(self, key: str, value: Any) -> None:
        """
        Set a command line override for a configuration value.
        
        Args:
            key: Config key (e.g., 'serial.port')
            value: Value to override with
        """
        self.command_line_overrides[key] = value
        
        # Notify callbacks if registered for this key
        if key in self.callbacks:
            old_value = self.get(key)
            for callback in self.callbacks[key]:
                callback(key, value, old_value)
    
    def clear_command_line_overrides(self) -> None:
        """Clear all command line overrides."""
        self.command_line_overrides = {}
    
    def _get_nested_value(self, data: Dict, key_path: List[str], default: Any = None) -> Any:
        """
        Get a nested value from a dictionary using a list of keys.
        
        Args:
            data: Dictionary to search in
            key_path: List of keys to traverse
            default: Default value if key not found
            
        Returns:
            The value at the key path, or default if not found
        """
        current = data
        for key in key_path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current
    
    def _set_nested_value(self, data: Dict, key_path: List[str], value: Any) -> None:
        """
        Set a nested value in a dictionary using a list of keys.
        Creates intermediate dictionaries as needed.
        
        Args:
            data: Dictionary to modify
            key_path: List of keys to traverse
            value: Value to set
        """
        current = data
        for i, key in enumerate(key_path):
            if i == len(key_path) - 1:
                current[key] = value
            else:
                if key not in current or not isinstance(current[key], dict):
                    current[key] = {}
                current = current[key]
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value, respecting overrides.
        
        Args:
            key: Configuration key (dot notation for nested values)
            default: Default value if key not found
            
        Returns:
            Configuration value or default if not found
        """
        # Check command line overrides first
        if key in self.command_line_overrides:
            return self.command_line_overrides[key]
        
        # Split key by dots for nested access
        key_path = key.split('.')
        return self._get_nested_value(self.config_data, key_path, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value in the config data.
        
        Args:
            key: Configuration key (dot notation for nested values)
            value: Value to set
        """
        # Don't set if there's a command line override
        if key in self.command_line_overrides:
            return
        
        # Get old value for callback
        old_value = self.get(key)
        
        # Set new value
        key_path = key.split('.')
        self._set_nested_value(self.config_data, key_path, value)
        
        # Notify callbacks if registered for this key
        if key in self.callbacks:
            for callback in self.callbacks[key]:
                callback(key, value, old_value)
    
    def register_callback(self, key: str, callback: Callable[[str, Any, Any], None]) -> None:
        """
        Register a callback to be notified when a config value changes.
        
        Args:
            key: Configuration key to watch
            callback: Function taking (key, new_value, old_value)
        """
        if key not in self.callbacks:
            self.callbacks[key] = []
        self.callbacks[key].append(callback)
    
    def unregister_callback(self, key: str, callback: Callable[[str, Any, Any], None]) -> None:
        """
        Unregister a previously registered callback.
        
        Args:
            key: Configuration key
            callback: Function to unregister
        """
        if key in self.callbacks and callback in self.callbacks[key]:
            self.callbacks[key].remove(callback)
            if not self.callbacks[key]:
                del self.callbacks[key]
