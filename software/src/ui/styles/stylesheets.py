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
class Stylesheets:
    # Main application stylesheet
    MAIN_STYLE = """
        QMainWindow {
            background-color: #5a5f61;
            border: 1px solid #5a5f61;
        }
        
        QTabWidget::pane {
            border: 0px;
            background-color: #7a7977;
        }
        
        QPushButton {
            border: none;
            padding: 6px 12px;
            border-radius: 3px;
            height: 20px;
        }
        
        QPushButton#samplingButtonRun {
            background-color: #66d9a8;
            color: white;
            font-weight: bold;
            padding: 8px 15px;
        }
        
        QPushButton#samplingButtonRun:hover {
            background-color: #5a5a5a;
            border: 2px solid #66d9a8;
            font-weight: bold;
            color: white;
        }
        
        QPushButton#samplingButtonRun:pressed {
            background-color: #3a3a3a;
            border: 2px solid #66d9a8;
            font-weight: bold;
            color: white;
        }

        QPushButton#samplingButtonStop {
            background-color: #ff5555;
            color: white;
            font-weight: bold;
            padding: 8px 15px;
        }

        QPushButton#samplingButtonStop:hover {
            background-color: #5a5a5a;
            border: 2px solid #ff5555;
            font-weight: bold;
            color: white;
        }

        QPushButton#samplingButtonStop:pressed {
            background-color: #3a3a3a;
            border: 2px solid #ff5555;
            font-weight: bold;
            color: white;
        }
        
        QLabel#connectionStatusLabel, QLabel#samplingStatusLabel {
            color: white;
            font-weight: bold;
            border-radius: 3px;
            padding: 5px;
        }
        
        QLabel#connectionStatusLabel[connected="true"], QLabel#samplingStatusLabel[running="true"] {
            background-color: #66d9a8; /* Green for connected/running */
        }
        
        QLabel#connectionStatusLabel[connected="false"], QLabel#samplingStatusLabel[running="false"] {
            background-color: #ff6b6b; /* Red for disconnected/stopped */
        }
        
        QLabel#sampleCountLabel, QLabel#bufferSizeLabel {
            color: white;
            background-color: #4a4a4a;
            border-radius: 3px;
            padding: 5px;
            font-weight: bold;
        }

        QPushButton#resetButton {
            background-color: #ff9800;  /* Orange for reset */
            color: white;
            font-weight: bold;
            padding: 8px 15px;
        }

        QPushButton#resetButton:hover {
            background-color: #5a5a5a;
            border: 2px solid #ff9800;
            color: white;
        }

        QPushButton#resetButton:pressed {
            background-color: #3a3a3a;
            border: 2px solid #ff9800;
            color: white;
        }

        QPushButton#exportButton {
            background-color: #2196F3;
            color: white;
            font-weight: bold;
            padding: 8px 15px;
        }

        QPushButton#exportButton:hover {
            background-color: #5a5a5a;
            border: 2px solid #2196F3;
            color: white;
        }

        QPushButton#exportButton:pressed {
            background-color: #3a3a3a;
            border: 2px solid #2196F3;
            color: white;
        }

        QPushButton#copyMdButton {
            background-color: #9C27B0;
            color: white;
            font-weight: bold;
            padding: 8px 15px;
        }

        QPushButton#copyMdButton:hover {
            background-color: #5a5a5a;
            border: 2px solid #9C27B0;
            color: white;
        }

        QPushButton#copyMdButton:pressed {
            background-color: #3a3a3a;
            border: 2px solid #9C27B0;
            color: white;
        }

        QWidget#headerWidget {
            background: none;
        }
    """
    
    # Style for table view
    TABLE_VIEW_STYLE = """
        QWidget {
            background-color: #ffffff;
        }
        
        QLabel {
            font-size: 12px;
        }

        QLabel#titleLabel {
            font-size: 18px;
            font-weight: bold;
            background: none;
            color: #FFFFFF;
            padding: 5px 0px;
        }

        QFrame#contentFrame {
            border-top: 1px solid #5a5f61;
            padding-top: 5px;
            background: none;
            border-bottom: 1px solid #5a5f61;
        }

        QFrame#sectionFrame {
            background: none;
            border-width: 0px 1px 0px 1px;
            border-style: solid;
            border-color: #5a5f61;
        }

        QLabel#railTitle {
            font-size: 14px;
            font-weight: bold;
            background: none;
            color: #FFFFFF;
            padding: 5px 0px;
        }

        QLabel#sectionTitle {
            font-size: 16px;
            font-weight: bold;
            background: none;
            color: #FFFFFF;
        }

        QLabel#columnHeader {
            font-size: 12px;
            font-weight: bold;
            background: #FFFFFF;
            color: #000000;
            border-bottom: 1px solid #5a5f61;
            padding: 2px 0px;
        }
        
        /* Styles for all Rail widget data cells */
        QLabel[objectName$="ColLabel"] {
            padding: 2px;
            border: 1px solid #e0e0e0;
            background-color: #f9f9f9;
        }

        /* Total Power Widget Styles */
        QLabel#totalPowerTitle {
            font-size: 16px;
            font-weight: bold;
            background: none;
            color: #FFFFFF;
            padding: 5px 0px;
            margin-bottom: 5px;
        }

        /* Style for the headers in Total Power (MIN, MAX, AVG, NOW) */
        QLabel[objectName$="Header"] {
            font-size: 14px;
            font-weight: bold;
            background: none;
            color: #000000;
            padding: 3px;
            background-color: #f9f9f9;
            border-bottom: 1px solid #5a5f61;
        }

        /* Style for the value labels in Total Power */
        QLabel[objectName$="Value"] {
            font-size: 14px;
            padding: 3px;
            background-color: #f9f9f9;
            color: #000000;
        }

        /* Give the Total Power widget a transparent background */
        QWidget#totalPowerWidget {
            background: none;
        }

        QWidget#rowWidget {
            background: none;
        }

        QWidget[objectName$="SectionWidget"] {
            background: none;
            border-style: solid;
            border-color: #5a5f61;
        }
    """