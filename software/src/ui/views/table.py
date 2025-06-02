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

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                          QPushButton, QFrame, QHBoxLayout)
from PyQt5.QtCore import Qt, pyqtSignal
import sys
import os

# Add the parent directory to sys.path to import from translations
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from styles.stylesheets import Stylesheets
from translations.strings import Strings

# Import Rail widget
from widgets.rail import Rail
# Import TotalPower widget
from widgets.total_power import TotalPower

class MainInterface(QWidget):
    # Define signals for button clicks
    sampling_button_clicked = pyqtSignal(bool)  # True when starting, False when stopping
    reset_button_clicked = pyqtSignal()  # Signal when reset button is clicked
    export_button_clicked = pyqtSignal()  # Signal when export button is clicked
    copy_md_button_clicked = pyqtSignal()  # Signal when copy markdown button is clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rails = {}  # Store references to all rail widgets
        self.total_power = None  # Store reference to total power widget
        self.is_sampling = False  # Track sampling state
        self.init_ui()
        
        # Initial state - buttons disabled until connection established
        self.enable_reset_button(False)
        self.enable_export_button(False)  # Export button initially disabled
        self.enable_copy_md_button(False)  # Copy MD button initially disabled
        
    def init_ui(self):
        # Create layout
        layout = QVBoxLayout()
        
        # Create header with title and run/stop button
        header_layout = QHBoxLayout()
        
        # Add a title
        title_label = QLabel(Strings.APP_TITLE)
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignLeft)
        header_layout.addWidget(title_label)
        
        # Add spacer to push button to the right
        header_layout.addStretch()
        
        # Add run/stop button
        self.sampling_button = QPushButton(Strings.BUTTON_RUN)
        self.sampling_button.setObjectName("samplingButtonRun")
        self.sampling_button.setFixedWidth(80)
        self.sampling_button.setFixedHeight(30)
        self.sampling_button.clicked.connect(self._on_sampling_button_clicked)
        self.sampling_button.setCursor(Qt.PointingHandCursor)
        self.sampling_button.setToolTip(Strings.TOOLTIP_START_SAMPLING)
        header_layout.addWidget(self.sampling_button)
        
        # Add reset button
        self.reset_button = QPushButton(Strings.BUTTON_RESET)
        self.reset_button.setObjectName("resetButton")
        self.reset_button.setFixedWidth(90)
        self.reset_button.setFixedHeight(30)
        self.reset_button.clicked.connect(self._on_reset_button_clicked)
        header_layout.addWidget(self.reset_button)
        
        # Add export button
        self.export_button = QPushButton(Strings.BUTTON_EXPORT)
        self.export_button.setObjectName("exportButton")
        self.export_button.setFixedWidth(90)
        self.export_button.setFixedHeight(30)
        self.export_button.clicked.connect(self._on_export_button_clicked)
        header_layout.addWidget(self.export_button)
        
        # Add copy markdown button
        self.copy_md_button = QPushButton(Strings.BUTTON_MARKDOWN)
        self.copy_md_button.setObjectName("copyMdButton")
        self.copy_md_button.setFixedWidth(120)
        self.copy_md_button.setFixedHeight(30)
        self.copy_md_button.clicked.connect(self._on_copy_md_button_clicked)
        header_layout.addWidget(self.copy_md_button)
        
        # Add header layout to main layout
        header_widget = QWidget()
        header_widget.setLayout(header_layout)
        header_widget.setObjectName("headerWidget")
        header_widget.setStyleSheet(Stylesheets.MAIN_STYLE)
        layout.addWidget(header_widget)
        
        # Create three sections for power rails
        section1 = self._create_section(Strings.SECTION_1, [
            Strings.SECTION_1_RAIL_1,
            Strings.SECTION_1_RAIL_2,
            Strings.SECTION_1_RAIL_3,
            Strings.SECTION_1_RAIL_4
        ])
        
        section2 = self._create_section(Strings.SECTION_2, [
            Strings.SECTION_2_RAIL_1,
            Strings.SECTION_2_RAIL_2,
            Strings.SECTION_2_RAIL_3
        ])
        
        section3 = self._create_section(Strings.SECTION_3, [
            Strings.SECTION_3_RAIL_1,
            Strings.SECTION_3_RAIL_2
        ])
        
        # Create main content widget with three columns
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_frame.setFrameShape(QFrame.StyledPanel)
        content_layout = QHBoxLayout(content_frame)
        content_layout.addWidget(section1)
        content_layout.addWidget(section2)
        content_layout.addWidget(section3)
        
        # Add components to main layout
        layout.addWidget(content_frame)
        
        # Add TotalPower widget below existing content without a background frame
        self.total_power = TotalPower()
        self.total_power.setObjectName("totalPowerWidget")
        layout.addWidget(self.total_power)
        
        layout.addStretch(1)
        
        self.setLayout(layout)
    
    def _on_sampling_button_clicked(self):
        # Toggle the status and emit signal
        self.is_sampling = not self.is_sampling
        # Note: We're not calling set_sampling_status here because that will be
        # triggered by MainWindow after the actual sampling state changes
        self.sampling_button_clicked.emit(self.is_sampling)
    
    def _on_reset_button_clicked(self):
        self.reset_button_clicked.emit()
    
    def _on_export_button_clicked(self):
        self.export_button_clicked.emit()
    
    def _on_copy_md_button_clicked(self):
        self.copy_md_button_clicked.emit()
    
    def set_sampling_status(self, is_running):
        self.is_sampling = is_running
        if is_running:
            self.sampling_button.setText(Strings.BUTTON_STOP)
            self.sampling_button.setObjectName("samplingButtonStop")
            self.sampling_button.setStyleSheet(Stylesheets.MAIN_STYLE)
            self.sampling_button.setCursor(Qt.PointingHandCursor)
            self.sampling_button.setToolTip(Strings.TOOLTIP_STOP_SAMPLING)
        else:
            self.sampling_button.setText(Strings.BUTTON_RUN)
            self.sampling_button.setObjectName("samplingButtonRun")
            self.sampling_button.setStyleSheet(Stylesheets.MAIN_STYLE)
            self.sampling_button.setCursor(Qt.PointingHandCursor)
            self.sampling_button.setToolTip(Strings.TOOLTIP_START_SAMPLING)
    
    def enable_sampling_button(self, enabled):
        self.sampling_button.setEnabled(enabled)
    
    def enable_reset_button(self, enabled):
        self.reset_button.setEnabled(enabled)
        self.reset_button.setCursor(Qt.PointingHandCursor if enabled else Qt.ArrowCursor)
        if enabled:
            self.reset_button.setToolTip(Strings.TOOLTIP_RESET_ENABLED)
        else:
            self.reset_button.setToolTip(Strings.TOOLTIP_RESET_DISABLED)
        
    def enable_export_button(self, enabled):
        self.export_button.setEnabled(enabled)
        self.export_button.setCursor(Qt.PointingHandCursor if enabled else Qt.ArrowCursor)
        if enabled:
            self.export_button.setToolTip(Strings.TOOLTIP_EXPORT_ENABLED)
        else:
            self.export_button.setToolTip(Strings.TOOLTIP_EXPORT_DISABLED)
        
    def enable_copy_md_button(self, enabled):
        self.copy_md_button.setEnabled(enabled)
        self.copy_md_button.setCursor(Qt.PointingHandCursor if enabled else Qt.ArrowCursor)
        if enabled:
            self.copy_md_button.setToolTip(Strings.TOOLTIP_MARKDOWN_ENABLED)
        else:
            self.copy_md_button.setToolTip(Strings.TOOLTIP_MARKDOWN_DISABLED)
        
    def _create_section(self, section_title, rail_names):
        section = QFrame()
        section.setObjectName("sectionFrame")
        section_layout = QVBoxLayout(section)
        section.setStyleSheet(Stylesheets.TABLE_VIEW_STYLE)
        
        # Add section title
        title = QLabel(section_title)
        title.setObjectName("sectionTitle")
        title.setAlignment(Qt.AlignCenter)
        section_layout.addWidget(title)
        
        # Add rails
        for rail_name in rail_names:
            rail = Rail(rail_name=rail_name)
            rail.setObjectName(f"rail_{rail_name.replace(' ', '_')}")
            section_layout.addWidget(rail)
            
            # Store reference to rail
            self.rails[rail_name] = rail
        
        section_layout.addStretch(1)
        return section
        
    def update_rail_data(self, rail_name, data_dict):
        if rail_name in self.rails:
            self.rails[rail_name].set_data(data_dict)
            
    def update_total_power(self, unit="W", min_val="0.0", max_val="0.0", avg_val="0.0", now_val="0.0"):
        if self.total_power:
            self.total_power.set_data(unit, min_val, max_val, avg_val, now_val)