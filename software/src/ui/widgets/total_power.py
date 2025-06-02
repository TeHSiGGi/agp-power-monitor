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

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from translations.strings import Strings
from styles.stylesheets import Stylesheets

class TotalPower(QWidget):
    """
    A widget to display total power information in a horizontal row.
    This widget shows min, max, avg, and current power values.
    """
    
    def __init__(self, parent=None):
        """
        Initialize the TotalPower widget.
        
        Args:
            parent: Parent widget
        """
        super(TotalPower, self).__init__(parent)
        
        self._data = {
            "unit": Strings.UNIT_POWER,
            "min": "0.0",
            "max": "0.0",
            "avg": "0.0", 
            "now": "0.0"
        }
        
        # Store references to labels for easy updates
        self._labels = {
            "unit": None,
            "min": None,
            "max": None,
            "avg": None,
            "now": None
        }
        
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout(self)
        main_layout.setObjectName("mainLayout")
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)
        
        # Create title label
        title_label = QLabel(Strings.TOTAL_POWER)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("totalPowerTitle")
        main_layout.addWidget(title_label)
        
        # Create horizontal layout for power values
        row_widget = QWidget()
        row_widget.setObjectName("rowWidget")
        row_widget.setStyleSheet(Stylesheets.TABLE_VIEW_STYLE)
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)
        
        # Create power data display
        sections = [
            {"name": "MIN", "key": "min", "label": Strings.SECTION_HEADING_MIN},
            {"name": "MAX", "key": "max", "label": Strings.SECTION_HEADING_MAX},
            {"name": "AVG", "key": "avg", "label": Strings.SECTION_HEADING_AVG},
            {"name": "NOW", "key": "now", "label": Strings.SECTION_HEADING_NOW}
        ]
        
        for section in sections:
            # Create container for each section
            section_widget = QWidget()
            section_widget.setObjectName(f"{section['name'].lower()}SectionWidget")
            section_layout = QVBoxLayout(section_widget)
            section_layout.setContentsMargins(0, 0, 0, 0)
            section_layout.setSpacing(0)
            
            # Create header for this section
            header_label = QLabel(section["label"])
            header_label.setAlignment(Qt.AlignCenter)
            header_label.setObjectName(f"{section['name'].lower()}Header")
            section_layout.addWidget(header_label)
            
            # Create value display
            value_label = QLabel(f"{self._data[section['key']]} {self._data['unit']}")
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setObjectName(f"{section['name'].lower()}Value")
            section_layout.addWidget(value_label)
            
            # Store reference to label
            self._labels[section["key"]] = value_label
            
            # Add section to row
            row_layout.addWidget(section_widget)
        
        main_layout.addWidget(row_widget)
        self.setLayout(main_layout)
        
    def set_data(self, unit=None, min_val="0.0", max_val="0.0", avg_val="0.0", now_val="0.0"):
        """
        Update all power data at once
        
        Args:
            unit (str): The unit of measurement (default: "W")
            min_val (str): Minimum power value
            max_val (str): Maximum power value
            avg_val (str): Average power value
            now_val (str): Current power value
        """
        # Use default unit from Strings if none provided
        if unit is None:
            unit = Strings.UNIT_POWER
            
        # Update internal data storage
        self._data["unit"] = unit
        self._data["min"] = min_val
        self._data["max"] = max_val
        self._data["avg"] = avg_val
        self._data["now"] = now_val
        
        # Update the corresponding labels
        for key in ["min", "max", "avg", "now"]:
            if self._labels[key]:
                self._labels[key].setText(f"{self._data[key]} {unit}")
    
    def get_data(self):
        """
        Get the current data
        
        Returns:
            dict: Current data dictionary
        """
        return self._data.copy()