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

import sys
import os
import platform
import argparse
import struct
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

# Add the parent directory to sys.path to import from translations
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ui.translations.strings import Strings
from ui.styles.stylesheets import Stylesheets

# Import our main interface (former TabA)
from ui.views.table import MainInterface

# Import StatusBar widget
from ui.widgets.status_bar import StatusBar

# Import MarkdownTableDialog
from ui.widgets.md_dialog import MarkdownTableDialog

# Import JSONDialog
from ui.widgets.json_dialog import JSONDialog

# Import hardware managers
from core.serial_manager import SerialManager
from core.data_manager import DataManager
from core.config_manager import ConfigManager

class MainWindow(QMainWindow):
    def __init__(self, config_manager, port=None, current_correction_factor=None, debug=None):
        super().__init__()
        
        # Store config manager
        self.config_manager = config_manager
        
        # Store command line configuration (these override config.yaml)
        if port is not None:
            self.config_manager.set_command_line_override('serial.port', port)
        if current_correction_factor is not None:
            self.config_manager.set_command_line_override('measurement.currentCorrectionFactor', current_correction_factor)
        if debug is not None:
            self.config_manager.set_command_line_override('debugLog', debug)
        
        # Get configuration values
        self.port = self.config_manager.get('serial.port')
        self.current_correction_factor = self.config_manager.get('measurement.currentCorrectionFactor', 1.0275)
        self.debug = self.config_manager.get('debugLog', False)
        self.ui_update_interval = self.config_manager.get('measurement.uiUpdateInterval', 100)
        
        if self.debug:
            print(f"Configuration loaded:")
            print(f"  - Port: {self.port}")
            print(f"  - Current Correction Factor: {self.current_correction_factor}")
            print(f"  - Debug: {self.debug}")
            print(f"  - UI Update Interval: {self.ui_update_interval}")
        
        # Initialize hardware managers with config
        self.serial_manager = SerialManager(config_manager=self.config_manager, current_correction_factor=self.current_correction_factor)
        self.data_manager = DataManager(config_manager=self.config_manager)
        
        # Initialize UI elements
        self.initUI()
        
        # Attempt connection on startup
        if not self.attempt_connection():
            # Show error message and exit the application
            QMessageBox.critical(self, Strings.MSG_CONNECTION_ERROR_TITLE, 
                                Strings.MSG_CONNECTION_ERROR)
            # Use a timer to allow the message box to be shown before quitting
            QTimer.singleShot(100, QApplication.instance().quit)
        
        self.poll_timer = None  # Timer for polling data manager
        
        # Start polling after UI is set up
        self.start_polling_data_manager()

    def initUI(self):
        # Set window title
        self.setWindowTitle(Strings.APP_TITLE)
        
        # Set window size (1024x600 as requested)
        self.resize(1024, 600)
        
        # Apply the main application stylesheet
        self.setStyleSheet(Stylesheets.MAIN_STYLE)

        # Set window icon from assets/logo.png
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'logo.png')
        print(f"Icon path: {icon_path}")  # Debugging line to check the icon path
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create the main interface (former TabA)
        self.main_interface = MainInterface()
        
        # Apply stylesheet to main interface
        self.main_interface.setStyleSheet(Stylesheets.TABLE_VIEW_STYLE)
        
        # Connect sampling button signal from main interface
        self.main_interface.sampling_button_clicked.connect(self.toggle_sampling)
        
        # Connect reset button signal from main interface
        self.main_interface.reset_button_clicked.connect(self.reset_buffer)
        
        # Connect export button signal from main interface
        self.main_interface.export_button_clicked.connect(self.export_data_to_csv)
        
        # Connect copy markdown button signal
        self.main_interface.copy_md_button_clicked.connect(self.copy_data_to_markdown)
        
        # Connect copy JSON button signal
        self.main_interface.copy_json_button_clicked.connect(self.copy_data_to_json)
        
        # Create status bar and pass the data_manager for state synchronization
        self.status_bar = StatusBar(parent=self, data_manager=self.data_manager)
        self.status_bar.setObjectName("statusBar")
        self.status_bar.setMaximumHeight(30)  # Limit height for the status bar
        
        # Add main interface and status bar to main layout
        layout.addWidget(self.main_interface)
        layout.addWidget(self.status_bar)
    
    # Helper methods to update status bar sections
    def set_connection_status(self, is_connected):
        """
        Update the connection status in the status bar
        
        Args:
            is_connected (bool): True if connected, False if disconnected
        """
        self.status_bar.set_connection_status(is_connected)
        # Enable/disable sampling and reset buttons based on connection status
        self.main_interface.enable_sampling_button(is_connected)
        self.main_interface.enable_reset_button(is_connected)
        
        # Export and Copy MD buttons should only be enabled if connected and not sampling
        self.main_interface.enable_export_button(is_connected and not self.data_manager.get_sampling())
        self.main_interface.enable_copy_md_button(is_connected and not self.data_manager.get_sampling())
        self.main_interface.enable_copy_json_button(is_connected and not self.data_manager.get_sampling())
        
    def set_sampling_status(self, is_running):
        """
        Update the sampling status in the status bar and main interface
        
        Args:
            is_running (bool): True if sampling is running, False if stopped
        """
        self.status_bar.set_sampling_status(is_running)
        self.main_interface.set_sampling_status(is_running)
        
        # Disable reset button when sampling is running
        # Only allow reset when connected but not sampling
        self.main_interface.enable_reset_button(self.data_manager.get_connected() and not is_running)
        
        # Enable export and copy md buttons only when NOT sampling and connected
        # Export should only be available when data collection is stopped
        self.main_interface.enable_export_button(self.data_manager.get_connected() and not is_running)
        self.main_interface.enable_copy_md_button(self.data_manager.get_connected() and not is_running)
        self.main_interface.enable_copy_json_button(self.data_manager.get_connected() and not is_running)
        
    def set_sample_count(self, samples_per_second):
        """
        Update the samples per second in the status bar
        
        Args:
            samples_per_second (float): Current samples per second rate
        """
        # Round to integer for display
        self.status_bar.set_sample_count(int(samples_per_second))
        
    def set_buffer_size(self, current_mb, max_mb=None):
        """
        Update the buffer size in the status bar
        
        Args:
            current_mb (float): Current buffer size in megabytes
            max_mb (float, optional): Maximum buffer size in megabytes
        """
        self.status_bar.set_buffer_size(current_mb, max_mb)

    def reset_buffer(self):
        """
        Reset the buffer and statistics in the data manager
        """
        # Only clear buffer if connected
        if not self.data_manager.get_connected():
            QMessageBox.warning(self, Strings.MSG_RESET_ERROR_TITLE, Strings.MSG_RESET_ERROR)
            return

        # Clear the data manager buffer
        self.data_manager.clear_buffer()
        
        # Update buffer size in status bar
        current_buffer_size = self.data_manager.get_buffer_size_mb()
        max_buffer_size = self.data_manager.get_max_buffer_size_mb()
        self.set_buffer_size(current_buffer_size, max_buffer_size)
        
        # If data is still being collected, display will update on next data packet
        # Otherwise, update all rails with zeros immediately
        if not self.data_manager.get_sampling():
            self._update_ui_with_zeros()
            
        print(Strings.DEBUG_BUFFER_RESET)
            
    def export_data_to_csv(self):
        """
        Export the buffer data to a CSV file
        """
        # Only allow export if connected and not sampling
        if not self.data_manager.get_connected():
            QMessageBox.warning(self, Strings.MSG_EXPORT_ERROR_TITLE, Strings.MSG_EXPORT_ERROR_NOT_CONNECTED)
            return
            
        if self.data_manager.get_sampling():
            QMessageBox.warning(self, Strings.MSG_EXPORT_ERROR_TITLE, Strings.MSG_EXPORT_ERROR_SAMPLING)
            return
            
        # Check if there is any data to export
        if self.data_manager.get_current_buffer_entries() == 0:
            QMessageBox.warning(self, Strings.MSG_EXPORT_ERROR_TITLE, Strings.MSG_EXPORT_ERROR_EMPTY)
            return
            
        # Import QFileDialog here to avoid polluting the global namespace
        from PyQt5.QtWidgets import QFileDialog
        
        # Open file dialog to select save location
        filename, _ = QFileDialog.getSaveFileName(
            self,
            Strings.FILE_DIALOG_EXPORT_TITLE,
            os.path.expanduser(Strings.FILE_DIALOG_DEFAULT_FILENAME),
            Strings.FILE_DIALOG_EXPORT_FILTER
        )
        
        # If a filename was provided (dialog not canceled)
        if filename:
            # Ensure it has a .csv extension
            if not filename.lower().endswith('.csv'):
                filename += '.csv'
            
            # Call the export_to_csv method
            if self.data_manager.export_to_csv(filename):
                QMessageBox.information(self, Strings.MSG_EXPORT_SUCCESS_TITLE, Strings.MSG_EXPORT_SUCCESS.format(filename))
            else:
                QMessageBox.critical(self, Strings.MSG_EXPORT_FAILED_TITLE, Strings.MSG_EXPORT_FAILED)
    
    def copy_data_to_markdown(self):
        """
        Create a markdown table with the rail data and copy it to the clipboard
        """
        # Only allow copying if connected and not sampling
        if not self.data_manager.get_connected():
            QMessageBox.warning(self, Strings.MSG_COPY_ERROR_TITLE, Strings.MSG_COPY_ERROR_NOT_CONNECTED)
            return
            
        if self.data_manager.get_sampling():
            QMessageBox.warning(self, Strings.MSG_COPY_ERROR_TITLE, Strings.MSG_COPY_ERROR_SAMPLING)
            return
            
        # Check if there is any data to copy
        if self.data_manager.get_current_buffer_entries() == 0:
            QMessageBox.warning(self, Strings.MSG_COPY_ERROR_TITLE, Strings.MSG_COPY_ERROR_EMPTY)
            return
            
        # Get total power data
        total_power_data = self.main_interface.total_power.get_data()
        
        # Create and show the dialog
        dialog = MarkdownTableDialog(self.main_interface.rails, total_power_data, self)
        dialog.exec_()
    
    def copy_data_to_json(self):
        """
        Create a JSON representation of the rail data and copy it to the clipboard
        """
        # Only allow copying if connected and not sampling
        if not self.data_manager.get_connected():
            QMessageBox.warning(self, Strings.MSG_COPY_ERROR_TITLE, Strings.MSG_COPY_ERROR_NOT_CONNECTED)
            return
            
        if self.data_manager.get_sampling():
            QMessageBox.warning(self, Strings.MSG_COPY_ERROR_TITLE, Strings.MSG_COPY_ERROR_SAMPLING)
            return
            
        # Check if there is any data to copy
        if self.data_manager.get_current_buffer_entries() == 0:
            QMessageBox.warning(self, Strings.MSG_COPY_ERROR_TITLE, Strings.MSG_COPY_ERROR_EMPTY)
            return
            
        # Get total power data
        total_power_data = self.main_interface.total_power.get_data()
        
        # Create and show the dialog
        dialog = JSONDialog(self.main_interface.rails, total_power_data, self)
        dialog.exec_()
    
    def _update_ui_with_zeros(self):
        """Update all rails and total power with zero values after buffer reset"""
        # Map rail index to UI rail names
        rail_map = [
            Strings.SECTION_3_RAIL_1,    # 0 ALTERNATIVE - Input A
            Strings.SECTION_3_RAIL_2,    # 1 ALTERNATIVE - Input B
            Strings.SECTION_1_RAIL_1,    # 2 AGP - 12V
            Strings.SECTION_1_RAIL_4,    # 3 AGP - VDDQ
            Strings.SECTION_1_RAIL_2,    # 4 AGP - 5V
            Strings.SECTION_1_RAIL_3,    # 5 AGP - 3.3V
            Strings.SECTION_2_RAIL_1,    # 6 EXTERNAL - 12V 6Pin
            Strings.SECTION_2_RAIL_2,    # 7 EXTERNAL - 12V 4Pin
            Strings.SECTION_2_RAIL_3,    # 8 EXTERNAL - 5V 4Pin
        ]
        
        # Reset all rail displays with zeros
        zero_data = {
            "voltage": {
                "unit": Strings.UNIT_VOLTAGE,
                "min": "0.000",
                "max": "0.000",
                "avg": "0.000",
                "now": "0.000",
            },
            "current": {
                "unit": Strings.UNIT_CURRENT,
                "min": "0.000",
                "max": "0.000",
                "avg": "0.000",
                "now": "0.000",
            },
            "power": {
                "unit": Strings.UNIT_POWER,
                "min": "0.000",
                "max": "0.000",
                "avg": "0.000",
                "now": "0.000",
            }
        }
        
        for rail_name in rail_map:
            self.main_interface.update_rail_data(rail_name, zero_data)
        
        # Reset total power display
        self.main_interface.update_total_power(
            unit=Strings.UNIT_POWER,
            min_val="0.000",
            max_val="0.000",
            avg_val="0.000",
            now_val="0.000"
        )
        
    def attempt_connection(self):
        """
        Attempt to connect to the serial port specified by the command line argument
        or from available ports if none specified.
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        # Use the port provided via command line
        selected_port = self.port
            
        # If no port configured, try to find an available port
        if not selected_port:
            # Get list of available ports
            available_ports = self.serial_manager.list_available_ports()
            if not available_ports:
                print("No serial ports available")
                return False
                
            # Try the first available port
            selected_port = available_ports[0]['device']
            print(f"No port specified, trying first available port: {selected_port}")
            
        # Try to connect with the specified or first available port
        if self.serial_manager.connect(port=selected_port):
            print(f"Connected to {selected_port}")
            # Update data manager and status bar
            self.data_manager.set_connected(True)
            # This will also update all relevant buttons
            self.set_connection_status(True)
            return True
        else:
            self.status_bar.set_connection_status(False)  # Reset the button state
            print(f"Failed to connect to {selected_port}")
            return False
    
    # Note: The toggle_connection method was removed as it's not being used in the codebase.
    # Importing struct module here to ensure it's available for the debug code that uses it
    import struct
    def toggle_sampling(self, should_sample):
        """
        Toggle the sampling state based on status bar button click
        
        Args:
            should_sample (bool): True to start sampling, False to stop sampling
        """
        if should_sample:
            # Double-check we can't start sampling if not connected
            if not self.data_manager.get_connected():
                self.set_sampling_status(False)  # Reset the button state
                QMessageBox.warning(self, Strings.MSG_SAMPLING_ERROR_TITLE, Strings.MSG_SAMPLING_ERROR_NOT_CONNECTED)
                return

            # Reset the data manager buffer before starting sampling
            self.data_manager.clear_buffer()
            # Wait a short moment to ensure UI and buffer are cleared before new data arrives
            QApplication.processEvents()
            QTimer.singleShot(50, lambda: self._start_sampling_sequence())
        else:
            # Send "P" command to stop sampling
            if self.serial_manager.send_data(b"P"):
                print("Sent command to stop sampling: P")
            
            # Stop sampling in the data manager
            if self.data_manager.get_sampling():
                self.data_manager.set_sampling(False)
                print("Stopping sampling")
                
                # Remove the callback
                self.serial_manager.set_data_callback(None)
                # Update status in both status bar and main interface
                self.set_sampling_status(False)

    def _start_sampling_sequence(self):
        """Helper to start sampling after buffer/UI clear delay."""
        # Send "S" command to start sampling
        if self.serial_manager.send_data(b"S"):
            print("Sent command to start sampling: S")
            # Try to start sampling in the data manager
            if self.data_manager.set_sampling(True):
                print("Starting sampling")
                # Delay assigning the data callback by 200ms
                self.set_sampling_status(True)
                QTimer.singleShot(200, lambda: self.serial_manager.set_data_callback(self.on_data_received))
            else:
                self.set_sampling_status(False)  # Reset the button state
        else:
            self.set_sampling_status(False)  # Reset the button state
            QMessageBox.warning(self, Strings.MSG_SAMPLING_ERROR_TITLE, Strings.MSG_SAMPLING_ERROR_CMD_FAILED)
    
    def on_data_received(self, data):
        """
        Process data received from the serial port
        
        Args:
            data (bytes): Raw data received from the serial port
        """
        # Debug output - display raw data in hex
        if self.debug and len(data) > 0:
            print(f"--- Received {len(data)} bytes ---")
            print(f"Raw data: {data.hex(' ')}")
        
        # Only process data if we're connected and sampling
        if not self.data_manager.get_connected() or not self.data_manager.get_sampling():
            return
        
        # Parse the incoming data using the SerialDataParser in serial_manager
        parsed_packages = self.serial_manager.parser.parse_data(data)
        
        # Define rail names for better debugging output
        rail_names = [
            "Input A",         # 0 ALTERNATIVE - Input A
            "Input B",         # 1 ALTERNATIVE - Input B
            "12V",             # 2 AGP - 12V
            "VDDQ",            # 3 AGP - VDDQ
            "5V",              # 4 AGP - 5V
            "3.3V",            # 5 AGP - 3.3V
            "12V 6pin",        # 6 EXTERNAL - 12V 6Pin
            "12V 4pin",        # 7 EXTERNAL - 12V 4Pin
            "5V 4pin",         # 8 EXTERNAL - 5V 4Pin
        ]
        
        # Debug output for parsed packages
        if self.debug:
            for package in parsed_packages:
                timestamp = package.get('timestamp', 0)
                sample_id = package.get('sample_id', 0)
                voltages = package.get('voltages', [])
                currents = package.get('currents', [])
                
                # Print package header
                print("\n--- Parsed Package ---")
                print(f"Timestamp: {timestamp} ({time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))})")
                print(f"Sample ID: {sample_id}")
                
                # Create bytearrays for voltage and current values
                voltage_bytes = bytearray()
                current_bytes = bytearray()
                for v in voltages:
                    voltage_bytes.extend(struct.pack('>H', v))  # Pack as big-endian unsigned short
                for c in currents:
                    current_bytes.extend(struct.pack('>h', c))  # Pack as big-endian signed short
                
                # Print table headers
                print("\nRail Values (hex):")
                print("┌───────────────┬───────────┬────────────┬───────────┬────────────┐")
                print("│ Rail Name     │ Voltage   │ Voltage    │ Current   │ Current    │")
                print("│               │ (decimal) │ (hex)      │ (decimal) │ (hex)      │")
                print("├───────────────┼───────────┼────────────┼───────────┼────────────┤")
                
                # Print values for each rail
                for i, rail in enumerate(rail_names):
                    if i < len(voltages) and i < len(currents):
                        v_hex = voltage_bytes[i*2:i*2+2].hex(' ')
                        c_hex = current_bytes[i*2:i*2+2].hex(' ')
                        print(f"│ {rail:<13} │ {voltages[i]:<9} │ {v_hex:<10} │ {currents[i]:<9} │ {c_hex:<10} │")
                print("└───────────────┴───────────┴────────────┴───────────┴────────────┘")
                
                # Print raw byte groups for the full package
                pkg_bytes = bytearray()
                pkg_bytes.extend(struct.pack('>I', timestamp))  # 4 bytes timestamp
                pkg_bytes.append(sample_id)  # 1 byte sample_id
                pkg_bytes.extend(voltage_bytes)  # 18 bytes voltages
                pkg_bytes.extend(current_bytes)  # 18 bytes currents
                
                print("\nPackage structure:")
                print(f"  [Timestamp]  : {pkg_bytes[0:4].hex(' ')}")
                print(f"  [Sample ID]  : {pkg_bytes[4:5].hex(' ')}")
                print(f"  [Voltages]   : {pkg_bytes[5:23].hex(' ')}")
                print(f"  [Currents]   : {pkg_bytes[23:41].hex(' ')}")
                print(f"  [CRC]        : (not included in parsed data)")
                print(f"  [End Marker] : FF 00 33 (fixed value)\n")
        
        # Process each parsed package
        for package in parsed_packages:
            # Each package should contain timestamp, sample_id, voltages, and currents
            voltages = package.get('voltages', [])
            currents = package.get('currents', [])
            
            # Insert the data into the data manager
            if len(voltages) == 9 and len(currents) == 9:
                # Convert from raw mV/mA to V/A if needed
                voltages_v = [v / 1000.0 for v in voltages]  # Convert from mV to V
                
                # Apply correction factor to current values and convert from mA to A
                currents_a = [(c / 1000.0) * self.current_correction_factor for c in currents]
                
                # Insert the data
                self.data_manager.insert_data(voltages_v, currents_a)
        
        # Update UI with current stats
        # Get sample rate directly from data manager
        samples_per_second = self.data_manager.get_packets_per_second()
        self.set_sample_count(samples_per_second)
        
        buffer_size = self.data_manager.get_buffer_size_mb()
        max_buffer_size = self.data_manager.get_max_buffer_size_mb()
        self.set_buffer_size(buffer_size, max_buffer_size)

    def start_polling_data_manager(self):
        """Start a timer to poll the data manager and update the UI."""
        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(self.ui_update_interval)
        self.poll_timer.timeout.connect(self.update_rails_from_data_manager)
        self.poll_timer.start()

    def update_rails_from_data_manager(self):
        """
        Poll the data manager and update the UI for all rails and total power.
        Rail order:
        0 ALTERNATIVE - Input A
        1 ALTERNATIVE - Input B
        2 AGP - 12V
        3 AGP - VDDQ
        4 AGP - 5V
        5 AGP - 3.3V
        6 EXTERNAL - 12V 6Pin
        7 EXTERNAL - 12V 4Pin
        8 EXTERNAL - 5V 4Pin
        """
        # Only update if we have data
        if self.data_manager.get_current_buffer_entries() == 0:
            return

        # Get the latest data entry
        data = self.data_manager.get_data()[-1]
        voltages = data['voltage']
        currents = data['current']
        powers = data['power']

        # Get stats for all rails
        stats = self.data_manager.get_all_stats()

        # Map rail index to UI rail names
        rail_map = [
            Strings.SECTION_3_RAIL_1,    # 0 ALTERNATIVE - Input A
            Strings.SECTION_3_RAIL_2,    # 1 ALTERNATIVE - Input B
            Strings.SECTION_1_RAIL_1,    # 2 AGP - 12V
            Strings.SECTION_1_RAIL_4,    # 3 AGP - VDDQ
            Strings.SECTION_1_RAIL_2,    # 4 AGP - 5V
            Strings.SECTION_1_RAIL_3,    # 5 AGP - 3.3V
            Strings.SECTION_2_RAIL_1,    # 6 EXTERNAL - 12V 6Pin
            Strings.SECTION_2_RAIL_2,    # 7 EXTERNAL - 12V 4Pin
            Strings.SECTION_2_RAIL_3,    # 8 EXTERNAL - 5V 4Pin
        ]

        for idx, rail_name in enumerate(rail_map):
            rail_data = {
                "voltage": {
                    "unit": Strings.UNIT_VOLTAGE,
                    "min": f"{stats['voltage']['min'][idx]:.3f}",
                    "max": f"{stats['voltage']['max'][idx]:.3f}",
                    "avg": f"{stats['voltage']['avg'][idx]:.3f}",
                    "now": f"{voltages[idx]:.3f}",
                },
                "current": {
                    "unit": Strings.UNIT_CURRENT,
                    "min": f"{stats['current']['min'][idx]:.3f}",
                    "max": f"{stats['current']['max'][idx]:.3f}",
                    "avg": f"{stats['current']['avg'][idx]:.3f}",
                    "now": f"{currents[idx]:.3f}",
                },
                "power": {
                    "unit": Strings.UNIT_POWER,
                    "min": f"{stats['power']['min'][idx]:.3f}",
                    "max": f"{stats['power']['max'][idx]:.3f}",
                    "avg": f"{stats['power']['avg'][idx]:.3f}",
                    "now": f"{powers[idx]:.3f}",
                }
            }
            self.main_interface.update_rail_data(rail_name, rail_data)

        # Update total power (sum of all rails)
        total_power = {
            "min": sum(stats['power']['min']),
            "max": sum(stats['power']['max']),
            "avg": sum(stats['power']['avg']),
            "now": sum(powers),
        }
        self.main_interface.update_total_power(
            unit=Strings.UNIT_POWER,
            min_val=f"{total_power['min']:.3f}",
            max_val=f"{total_power['max']:.3f}",
            avg_val=f"{total_power['avg']:.3f}",
            now_val=f"{total_power['now']:.3f}",
        )

    def closeEvent(self, event):
        """
        Handle the window close event
        
        Args:
            event: The close event
        """
        # Send the stop command "P" when closing the application
        if self.data_manager.get_connected():
            if self.serial_manager.send_data(b"P"):
                print("Sent stop command on exit: P")
        
        # Disconnect from serial port before exiting
        self.serial_manager.disconnect()
        
        # Stop polling timer
        if self.poll_timer:
            self.poll_timer.stop()
        
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='AGP Power Monitor')
    parser.add_argument('port', nargs='?', help='Serial port to connect to')
    parser.add_argument('--correction-factor', '-c', type=float,
                        help='Current correction factor (overrides config.yaml)')
    parser.add_argument('--debug', '-d', action='store_true',
                        help='Enable debug output')
    parser.add_argument('--baudrate', '-b', type=int,
                        help='Serial baudrate (overrides config.yaml)')
    parser.add_argument('--config', type=str,
                        help='Path to config.yaml file')
    args = parser.parse_args()
    
    # Initialize the configuration manager
    config_manager = ConfigManager(args.config)
    
    # Set application icon specifically for macOS dock
    icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'logo.png')
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
        
        # Special handling for macOS dock icon
        if platform.system() == "Darwin":  # Darwin is the name for macOS
            import PyQt5.QtCore
            PyQt5.QtCore.QCoreApplication.setAttribute(Qt.AA_DontShowIconsInMenus, False)
            app.setAttribute(Qt.AA_DontShowIconsInMenus, False)
    
    # Create main window with config manager and parsed arguments
    mainWindow = MainWindow(config_manager=config_manager, 
                           port=args.port, 
                           current_correction_factor=args.correction_factor, 
                           debug=args.debug)
    mainWindow.show()
    sys.exit(app.exec_())