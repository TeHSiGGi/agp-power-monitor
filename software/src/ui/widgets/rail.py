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

from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from translations.strings import Strings

class Rail(QWidget):
    """
    A widget to display power rail information.
    This widget shows voltage, current, and power data in a grid format.
    The data is displayed in a 3x5 grid with headers for each column.
    -------------------------
    """
    
    def __init__(self, rail_name="Rail", parent=None):
        """
        Initialize the Rail widget.
        
        Args:
            rail_name (str): The name of the power rail
            parent: Parent widget
        """
        super(Rail, self).__init__(parent)
        
        self.rail_name = rail_name
        self._data = {
            "voltage": {"unit": Strings.UNIT_VOLTAGE, "min": "0.0", "max": "0.0", "avg": "0.0", "now": "0.0"},
            "current": {"unit": Strings.UNIT_CURRENT, "min": "0.0", "max": "0.0", "avg": "0.0", "now": "0.0"},
            "power": {"unit": Strings.UNIT_POWER, "min": "0.0", "max": "0.0", "avg": "0.0", "now": "0.0"}
        }
        
        # Store references to labels for easy updates
        self._labels = {
            "voltage": {"unit": None, "min": None, "max": None, "avg": None, "now": None},
            "current": {"unit": None, "min": None, "max": None, "avg": None, "now": None},
            "power": {"unit": None, "min": None, "max": None, "avg": None, "now": None}
        }
        
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout(self)
        main_layout.setObjectName("mainLayout")
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        
        # Create rail name label
        title_label = QLabel(self.rail_name)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("railTitle")
        main_layout.addWidget(title_label)
        
        # Create grid widget and layout
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setContentsMargins(0,0,0,0)
        grid_layout.setSpacing(0)
        
        # Create column headers
        headers = [
            Strings.SECTION_HEADING_UNIT,
            Strings.SECTION_HEADING_MIN,
            Strings.SECTION_HEADING_MAX,
            Strings.SECTION_HEADING_AVG,
            Strings.SECTION_HEADING_NOW
        ]
        
        for col, header in enumerate(headers):
            label = QLabel(header)
            label.setAlignment(Qt.AlignCenter)
            label.setObjectName("columnHeader")
            grid_layout.addWidget(label, 0, col)
        
        # Create data grid (3 rows x 5 columns)
        row_types = ["voltage", "current", "power"]
        col_types = ["unit", "min", "max", "avg", "now"]
        
        for row, row_type in enumerate(row_types):
            for col, col_type in enumerate(col_types):
                # Create label for this cell
                label = QLabel(self._data[row_type][col_type])
                label.setAlignment(Qt.AlignCenter)
                label.setObjectName(f"{row_type}{col_type.capitalize()}ColLabel")
                
                # Store reference to label
                self._labels[row_type][col_type] = label
                
                # Add to layout (row+1 because we have headers)
                grid_layout.addWidget(label, row+1, col)
        
        main_layout.addWidget(grid_widget)
        self.setLayout(main_layout)
        
    def set_rail_name(self, name):
        """
        Set the rail name
        
        Args:
            name (str): The name to display
        """
        # Find the title label in the layout
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QLabel) and widget.objectName() == "railTitle":
                widget.setText(name)
                break
        
        self.rail_name = name
    
    def set_data(self, data_dict):
        """
        Update all data at once using a dictionary
        
        Args:
            data_dict (dict): Dictionary containing the data to display
                Example format:
                {
                    "voltage": {"unit": "V", "min": "11.9", "max": "12.1", "avg": "12.0", "now": "12.0"},
                    "current": {"unit": "A", "min": "0.5", "max": "2.0", "avg": "1.2", "now": "1.1"},
                    "power": {"unit": "W", "min": "6.0", "max": "24.2", "avg": "14.4", "now": "13.2"}
                }
        """
        # Update internal data storage
        for data_type in data_dict:
            if data_type in self._data:
                for value_type in data_dict[data_type]:
                    if value_type in self._data[data_type]:
                        self._data[data_type][value_type] = data_dict[data_type][value_type]
                        
                        # Update the corresponding label
                        if self._labels[data_type][value_type]:
                            self._labels[data_type][value_type].setText(str(data_dict[data_type][value_type]))
    
    def set_voltage(self, unit=None, min_val="0.0", max_val="0.0", avg_val="0.0", now_val="0.0"):
        """Set voltage values"""
        if unit is None:
            unit = Strings.UNIT_VOLTAGE
        data = {"voltage": {"unit": unit, "min": min_val, "max": max_val, "avg": avg_val, "now": now_val}}
        self.set_data(data)
    
    def set_current(self, unit=None, min_val="0.0", max_val="0.0", avg_val="0.0", now_val="0.0"):
        """Set current values"""
        if unit is None:
            unit = Strings.UNIT_CURRENT
        data = {"current": {"unit": unit, "min": min_val, "max": max_val, "avg": avg_val, "now": now_val}}
        self.set_data(data)
    
    def set_power(self, unit=None, min_val="0.0", max_val="0.0", avg_val="0.0", now_val="0.0"):
        """Set power values"""
        if unit is None:
            unit = Strings.UNIT_POWER
        data = {"power": {"unit": unit, "min": min_val, "max": max_val, "avg": avg_val, "now": now_val}}
        self.set_data(data)
    
    def get_data(self):
        """
        Get the current data
        
        Returns:
            dict: Current data dictionary
        """
        return self._data.copy()