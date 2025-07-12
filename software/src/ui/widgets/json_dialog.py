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

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, 
                             QCheckBox, QGroupBox, QDialogButtonBox)
from PyQt5.QtCore import Qt
import pyperclip
import json
from ui.translations.strings import Strings

class JSONDialog(QDialog):
    def __init__(self, rail_data, total_power_data, parent=None):
        super().__init__(parent)
        
        self.rail_data = rail_data
        self.total_power_data = total_power_data
        
        self.selected_rails = {}
        
        self.setWindowTitle(Strings.JSON_DIALOG_TITLE)
        self.setMinimumWidth(400)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel(Strings.JSON_INSTRUCTIONS)
        layout.addWidget(instructions)
        
        # Rails selection group
        rails_group = QGroupBox(Strings.JSON_RAILS_GROUP)
        rails_layout = QVBoxLayout(rails_group)
        
        # Add checkboxes for all rails
        for rail_name, rail_widget in self.rail_data.items():
            checkbox = QCheckBox(rail_name)
            checkbox.setChecked(True)  # Pre-select all rails
            checkbox.stateChanged.connect(self.update_rail_selection)
            rails_layout.addWidget(checkbox)
            self.selected_rails[rail_name] = True
        
        layout.addWidget(rails_group)
        
        # Preview section
        preview_label = QLabel(Strings.JSON_PREVIEW_LABEL)
        preview_label.setWordWrap(True)
        layout.addWidget(preview_label)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).setText(Strings.JSON_COPY_BUTTON)
        button_box.accepted.connect(self.copy_to_clipboard)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def update_rail_selection(self, state):
        # Get the sender (checkbox)
        checkbox = self.sender()
        self.selected_rails[checkbox.text()] = (state == Qt.Checked)
    
    def generate_json(self):
        # Create dictionary for JSON output
        output = {
            "rails": [],
            "totalPower": {}
        }
        
        # Get selected rails data
        for rail_name, is_selected in self.selected_rails.items():
            if is_selected and rail_name in self.rail_data:
                rail_data = self.rail_data[rail_name].get_data()
                
                # Extract and format the rail data
                rail_json = {
                    "name": rail_name,
                    "voltage": {
                        "min": float(rail_data["voltage"]["min"]),
                        "max": float(rail_data["voltage"]["max"]),
                        "average": float(rail_data["voltage"]["avg"])
                    },
                    "current": {
                        "min": float(rail_data["current"]["min"]),
                        "max": float(rail_data["current"]["max"]),
                        "average": float(rail_data["current"]["avg"])
                    },
                    "power": {
                        "min": float(rail_data["power"]["min"]),
                        "max": float(rail_data["power"]["max"]),
                        "average": float(rail_data["power"]["avg"])
                    }
                }
                
                output["rails"].append(rail_json)
        
        # Add total power data
        output["totalPower"] = {
            "min": float(self.total_power_data["min"]),
            "max": float(self.total_power_data["max"]),
            "average": float(self.total_power_data["avg"])
        }
        
        # Convert to JSON string with indentation for readability
        return json.dumps(output, indent=4)
    
    def copy_to_clipboard(self):
        json_text = self.generate_json()
        pyperclip.copy(json_text)
        self.accept()