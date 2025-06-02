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
from ui.translations.strings import Strings

class MarkdownTableDialog(QDialog):
    def __init__(self, rail_data, total_power_data, parent=None):
        super().__init__(parent)
        
        self.rail_data = rail_data
        self.total_power_data = total_power_data
        
        self.selected_rails = {}
        self.include_header = True
        
        self.setWindowTitle(Strings.MARKDOWN_DIALOG_TITLE)
        self.setMinimumWidth(400)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel(Strings.MARKDOWN_INSTRUCTIONS)
        layout.addWidget(instructions)
        
        # Rails selection group
        rails_group = QGroupBox(Strings.MARKDOWN_RAILS_GROUP)
        rails_layout = QVBoxLayout(rails_group)
        
        # Add checkboxes for all rails
        for rail_name, rail_widget in self.rail_data.items():
            checkbox = QCheckBox(rail_name)
            checkbox.setChecked(True)  # Pre-select all rails
            checkbox.stateChanged.connect(self.update_rail_selection)
            rails_layout.addWidget(checkbox)
            self.selected_rails[rail_name] = True
        
        layout.addWidget(rails_group)
        
        # Options group
        options_group = QGroupBox(Strings.MARKDOWN_OPTIONS_GROUP)
        options_layout = QVBoxLayout(options_group)
        
        # Option to include header
        self.header_checkbox = QCheckBox(Strings.MARKDOWN_INCLUDE_HEADER)
        self.header_checkbox.setChecked(True)
        options_layout.addWidget(self.header_checkbox)
        
        layout.addWidget(options_group)
        
        # Preview section
        preview_label = QLabel(Strings.MARKDOWN_PREVIEW_LABEL)
        preview_label.setWordWrap(True)
        layout.addWidget(preview_label)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).setText(Strings.MARKDOWN_COPY_BUTTON)
        button_box.accepted.connect(self.copy_to_clipboard)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def update_rail_selection(self, state):
        # Get the sender (checkbox)
        checkbox = self.sender()
        self.selected_rails[checkbox.text()] = (state == Qt.Checked)
    
    def generate_markdown_table(self):
        markdown = ""
        include_header = self.header_checkbox.isChecked()
        
        # Get selected rails data
        selected_rail_data = {}
        for rail_name, is_selected in self.selected_rails.items():
            if is_selected and rail_name in self.rail_data:
                selected_rail_data[rail_name] = self.rail_data[rail_name].get_data()
        
        # Start building the header row with rail names
        header = "| Power |"
        separator = "|-------|"
        
        # Build the data row with AVG (MIN/MAX) format
        values_row = "| AVG (MIN/MAX) |"
        
        # Add each selected rail as a column
        for rail_name, rail_data in selected_rail_data.items():
            power_data = rail_data["power"]
            header += f" {rail_name} |"
            separator += "--------|"
            values_row += f" {power_data['avg']} ({power_data['min']}/{power_data['max']}) |"
        
        # Add total power column
        header += " **Total Power** |"
        separator += "-----------|"
        values_row += f"**{self.total_power_data['avg']} ({self.total_power_data['min']}/{self.total_power_data['max']})** |"
        
        # Assemble the final markdown
        if include_header:
            markdown = header + "\n" + separator + "\n"
        
        markdown += values_row + "\n"
        
        return markdown
    
    def copy_to_clipboard(self):
        markdown = self.generate_markdown_table()
        pyperclip.copy(markdown)
        self.accept()
