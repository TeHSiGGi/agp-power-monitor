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

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from styles.stylesheets import Stylesheets
from ui.translations.strings import Strings

class StatusBar(QWidget):
    """
    A widget to display application status information.
    This widget shows connection status, sampling status, buffer sample count, and buffer size.
    """
    def __init__(self, parent=None, data_manager=None):
        """
        Initialize the StatusBar widget.
        
        Args:
            parent: Parent widget
            data_manager: Optional DataManager instance to sync status with
        """
        super(StatusBar, self).__init__(parent)
        
        # Set object name for CSS styling
        self.setObjectName("statusBar")
        
        # Apply stylesheet
        self.setStyleSheet(Stylesheets.MAIN_STYLE)
        
        self.data_manager = data_manager
        
        # Initialize status data
        self._data = {
            "connection": {"status": False, "text": Strings.STATUS_BAR_DISCONNECTED},
            "sampling": {"status": False, "text": Strings.STATUS_BAR_STOPPED},
            "sample_count": 0,
            "buffer_size": {"current": 0, "max": 100} # MB
        }
        
        # If data manager is provided, get initial states from it
        if self.data_manager:
            self._data["connection"]["status"] = self.data_manager.get_connected()
            self._data["connection"]["text"] = Strings.STATUS_BAR_CONNECTED if self.data_manager.get_connected() else Strings.STATUS_BAR_DISCONNECTED
            self._data["sampling"]["status"] = self.data_manager.get_sampling()
            self._data["sampling"]["text"] = Strings.STATUS_BAR_RUNNING if self.data_manager.get_sampling() else Strings.STATUS_BAR_STOPPED
        
        # Store references to labels for easy updates
        self._labels = {
            "connection": None,
            "sampling": None,
            "sample_count": None,
            "buffer_size": None
        }
        
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI components"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 3, 5, 3)
        main_layout.setSpacing(10)
        
        # Create connection status label
        connection_label = QLabel(self._data["connection"]["text"])
        connection_label.setObjectName("connectionStatusLabel")
        connection_label.setAlignment(Qt.AlignCenter)
        connection_label.setMinimumWidth(100)
        # Set initial connection status property
        connection_label.setProperty("connected", "true" if self._data["connection"]["status"] else "false")
        connection_label.style().unpolish(connection_label)
        connection_label.style().polish(connection_label)
        main_layout.addWidget(connection_label)
        self._labels["connection"] = connection_label
        
        # Create sampling status label
        sampling_label = QLabel(self._data["sampling"]["text"])
        sampling_label.setObjectName("samplingStatusLabel")
        # Set initial sampling status property
        sampling_label.setProperty("running", "true" if self._data["sampling"]["status"] else "false")
        sampling_label.style().unpolish(sampling_label)
        sampling_label.style().polish(sampling_label)
        sampling_label.setAlignment(Qt.AlignCenter)
        sampling_label.setMinimumWidth(100)
        main_layout.addWidget(sampling_label)
        self._labels["sampling"] = sampling_label
        
        # Create sample count label (samples per second)
        sample_count_label = QLabel(f"{Strings.STATUS_BAR_SAMPLES_PER_SECOND}: {self._data['sample_count']}")
        sample_count_label.setObjectName("sampleCountLabel")
        sample_count_label.setAlignment(Qt.AlignCenter)
        sample_count_label.setMinimumWidth(100)
        main_layout.addWidget(sample_count_label)
        self._labels["sample_count"] = sample_count_label
        
        # Create buffer size label with two decimal places
        buffer_size_label = QLabel(
            f"{Strings.STATUS_BAR_BUFFER}: {self._data['buffer_size']['current']:.2f} / {self._data['buffer_size']['max']:.2f} {Strings.STATUS_BAR_MB}"
        )
        buffer_size_label.setObjectName("bufferSizeLabel")
        buffer_size_label.setAlignment(Qt.AlignCenter)
        buffer_size_label.setMinimumWidth(150)
        main_layout.addWidget(buffer_size_label)
        self._labels["buffer_size"] = buffer_size_label
        
        # Add a spacer to push everything to the left
        main_layout.addStretch(1)
        
        self.setLayout(main_layout)
    
    def set_connection_status(self, is_connected):
        """
        Set the connection status
        
        Args:
            is_connected (bool): True if connected, False if disconnected
        """
        self._data["connection"]["status"] = is_connected
        self._data["connection"]["text"] = Strings.STATUS_BAR_CONNECTED if is_connected else Strings.STATUS_BAR_DISCONNECTED
        
        # Update data manager if available
        if self.data_manager:
            self.data_manager.set_connected(is_connected)
        
        if self._labels["connection"]:
            self._labels["connection"].setText(self._data["connection"]["text"])
            # Update property and refresh style
            self._labels["connection"].setProperty("connected", "true" if is_connected else "false")
            self._labels["connection"].style().unpolish(self._labels["connection"])
            self._labels["connection"].style().polish(self._labels["connection"])
    
    def set_sampling_status(self, is_running):
        """
        Set the sampling status
        
        Args:
            is_running (bool): True if sampling is running, False if stopped
        """
        self._data["sampling"]["status"] = is_running
        self._data["sampling"]["text"] = Strings.STATUS_BAR_RUNNING if is_running else Strings.STATUS_BAR_STOPPED
        
        # Update data manager if available
        if self.data_manager:
            # Note: set_sampling may fail if we're not connected
            if is_running and not self.data_manager.set_sampling(is_running):
                # If setting sampling to True failed, keep UI showing as stopped
                self._data["sampling"]["status"] = False
                self._data["sampling"]["text"] = Strings.STATUS_BAR_STOPPED
                is_running = False
            else:
                self.data_manager.set_sampling(is_running)
        
        if self._labels["sampling"]:
            self._labels["sampling"].setText(self._data["sampling"]["text"])
            # Update property and refresh style
            self._labels["sampling"].setProperty("running", "true" if is_running else "false")
            self._labels["sampling"].style().unpolish(self._labels["sampling"])
            self._labels["sampling"].style().polish(self._labels["sampling"])
    
    def set_sample_count(self, count):
        """
        Set the sample count
        
        Args:
            count (int): The current samples per second
        """
        self._data["sample_count"] = count
        
        if self._labels["sample_count"]:
            self._labels["sample_count"].setText(f"{Strings.STATUS_BAR_SAMPLES_PER_SECOND}: {count}")
    
    def set_buffer_size(self, current_mb, max_mb=None):
        """
        Set the buffer size
        
        Args:
            current_mb (float): The current buffer size in MB
            max_mb (float, optional): The maximum buffer size in MB
        """
        self._data["buffer_size"]["current"] = current_mb
        
        if max_mb is not None:
            self._data["buffer_size"]["max"] = max_mb
        
        if self._labels["buffer_size"]:
            self._labels["buffer_size"].setText(
                f"{Strings.STATUS_BAR_BUFFER}: {self._data['buffer_size']['current']:.2f} {Strings.STATUS_BAR_OF} {self._data['buffer_size']['max']:.2f} {Strings.STATUS_BAR_MB}"
            )
    
    def get_status(self):
        """
        Get the current status
        
        Returns:
            dict: Current status dictionary
        """
        return self._data.copy()