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

class Strings:
    """
    This class contains all the strings used in the UI.
    """
    
    ## Application general strings ##
    APP_TITLE = "AGP Power Monitor"

    ## Tab A specific strings ##
    # General strings
    TITLE_LABEL = "Data Overview"
    SECTION_1 = "AGP"
    SECTION_2 = "EXTERNAL"
    SECTION_3 = "ALTERNATIVE"
    TOTAL_POWER = "Total Power"

    # Button labels
    BUTTON_RUN = "RUN"
    BUTTON_STOP = "STOP"
    BUTTON_RESET = "RESET"
    BUTTON_EXPORT = "EXPORT"
    BUTTON_MARKDOWN = "MARKDOWN"
    
    # Button tooltips
    TOOLTIP_START_SAMPLING = "Click to start sampling"
    TOOLTIP_STOP_SAMPLING = "Click to stop sampling"
    TOOLTIP_RESET_ENABLED = "Click to reset all data and clear buffer"
    TOOLTIP_RESET_DISABLED = "Reset disabled until sampling is stopped"
    TOOLTIP_EXPORT_ENABLED = "Click to export data as CSV"
    TOOLTIP_EXPORT_DISABLED = "Export disabled until sampling is stopped"
    TOOLTIP_MARKDOWN_ENABLED = "Click to copy data as Markdown table"
    TOOLTIP_MARKDOWN_DISABLED = "Copy Markdown disabled until sampling is stopped"

    # Section headings
    SECTION_HEADING_UNIT = "Unit"
    SECTION_HEADING_MIN = "Min"
    SECTION_HEADING_MAX = "Max"
    SECTION_HEADING_AVG = "Avg"
    SECTION_HEADING_NOW = "Now"
    
    # Units
    UNIT_VOLTAGE = "V"
    UNIT_CURRENT = "A"
    UNIT_POWER = "W"

    # Section 1 strings
    SECTION_1_RAIL_1 = "12V"
    SECTION_1_RAIL_2 = "5V"
    SECTION_1_RAIL_3 = "3.3V"
    SECTION_1_RAIL_4 = "VDDQ"

    # Section 2 strings
    SECTION_2_RAIL_1 = "12V 6pin"
    SECTION_2_RAIL_2 = "12V 4pin"
    SECTION_2_RAIL_3 = "5V 4pin"

    # Section 3 strings
    SECTION_3_RAIL_1 = "Input A"
    SECTION_3_RAIL_2 = "Input B"

    # Markdown dialog strings
    MARKDOWN_DIALOG_TITLE = "Copy Markdown Table"
    MARKDOWN_INSTRUCTIONS = "Select rails to include in the markdown table:"
    MARKDOWN_RAILS_GROUP = "Rails"
    MARKDOWN_OPTIONS_GROUP = "Options"
    MARKDOWN_INCLUDE_HEADER = "Include header row"
    MARKDOWN_PREVIEW_LABEL = "The markdown table will be copied to clipboard when you click 'Copy'."
    MARKDOWN_COPY_BUTTON = "Copy"

    # Status bar strings
    STATUS_BAR_RUNNING = "Running"
    STATUS_BAR_STOPPED = "Stopped"
    STATUS_BAR_CONNECTED = "Connected"
    STATUS_BAR_DISCONNECTED = "Disconnected"
    STATUS_BAR_SAMPLES_PER_SECOND = "Samples/s"
    STATUS_BAR_BUFFER = "Buffer"
    STATUS_BAR_MB = "MB"
    STATUS_BAR_OF = "of"
    
    # Message box strings
    MSG_CONNECTION_ERROR_TITLE = "Connection Error"
    MSG_CONNECTION_ERROR = "Failed to establish connection to the device. Please check your connection and restart the application."
    MSG_RESET_ERROR_TITLE = "Reset Error"
    MSG_RESET_ERROR = "Cannot reset buffer - not connected to serial port."
    MSG_EXPORT_ERROR_TITLE = "Export Error"
    MSG_EXPORT_ERROR_NOT_CONNECTED = "Cannot export data - not connected to serial port."
    MSG_EXPORT_ERROR_SAMPLING = "Cannot export data while sampling is running. Stop sampling first."
    MSG_EXPORT_ERROR_EMPTY = "No data to export. Buffer is empty."
    MSG_EXPORT_SUCCESS_TITLE = "Export Successful"
    MSG_EXPORT_SUCCESS = "Data successfully exported to:\n{0}"
    MSG_EXPORT_FAILED_TITLE = "Export Failed"
    MSG_EXPORT_FAILED = "Failed to export data. Check file permissions and disk space."
    MSG_COPY_ERROR_TITLE = "Copy Error"
    MSG_COPY_ERROR_NOT_CONNECTED = "Cannot copy data - not connected to serial port."
    MSG_COPY_ERROR_SAMPLING = "Cannot copy data while sampling is running. Stop sampling first."
    MSG_COPY_ERROR_EMPTY = "No data to copy. Buffer is empty."
    MSG_SAMPLING_ERROR_TITLE = "Sampling Error"
    MSG_SAMPLING_ERROR_NOT_CONNECTED = "Cannot start sampling - not connected to serial port."
    MSG_SAMPLING_ERROR_CMD_FAILED = "Failed to send start command to device."
    
    # File dialog strings
    FILE_DIALOG_EXPORT_TITLE = "Save Data As CSV"
    FILE_DIALOG_EXPORT_FILTER = "CSV Files (*.csv);;All Files (*)"
    FILE_DIALOG_DEFAULT_FILENAME = "~/Desktop/power_data.csv"
    
    # Icon and debug strings
    DEBUG_BUFFER_RESET = "Buffer reset complete"