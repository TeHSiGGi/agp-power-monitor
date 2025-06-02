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

import serial
import serial.tools.list_ports
from typing import List, Dict, Optional, Callable
import threading
import time
from core.serial_parser import SerialDataParser


class SerialManager:
    """
    Manages serial port connections, listing available ports,
    connecting/disconnecting, and handling incoming data.
    """
    
    def __init__(self, config_manager=None, current_correction_factor=1.0275):
        """
        Initialize the SerialManager.
        
        Args:
            config_manager: Optional ConfigManager instance for centralized settings
            current_correction_factor: Correction factor to apply to current measurements (default: 1.0275)
        """
        self.serial_connection: Optional[serial.Serial] = None
        self.is_connected = False
        self.read_thread: Optional[threading.Thread] = None
        self.stop_thread = False
        self.data_callback: Optional[Callable[[bytes], None]] = None
        self.parser = SerialDataParser()  # Initialize the data parser
        self.current_correction_factor = current_correction_factor
        
        # Store config manager
        self.config_manager = config_manager
    
    def list_available_ports(self) -> List[Dict[str, str]]:
        """
        List all available serial ports on the system.
        
        Returns:
            List of dictionaries containing port information (device, name, description)
        """
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append({
                'device': port.device,
                'name': port.name,
                'description': port.description
            })
        return ports
    
    def connect(self, port: str = None, baudrate: int = None, timeout: float = None) -> bool:
        """
        Connect to the specified serial port.
        If settings_manager is available, it will use settings from there.
        
        Args:
            port: The port name/path to connect to (or None to use settings)
            baudrate: Baud rate for the connection (or None to use settings)
            timeout: Read timeout in seconds (or None to use settings)
            
        Returns:
            True if connection successful, False otherwise
        """
        # Disconnect if already connected
        if self.is_connected:
            self.disconnect()
        
        # Use settings from config manager if available
        if self.config_manager:
            # Only override if params are None
            if port is None:
                port = self.config_manager.get("serial.port")
            if baudrate is None:
                baudrate = self.config_manager.get("serial.baudrate", 115200)
            if timeout is None:
                timeout = self.config_manager.get("serial.timeout", 1.0)
        
        # Default values if still None
        if port is None:
            print("Error: No port specified for connection")
            return False
        if baudrate is None:
            baudrate = 115200
        if timeout is None:
            timeout = 1.0
            
        try:
            self.serial_connection = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout
            )
            self.is_connected = True
            
            # Send "R<EPOCH>" command after successful connection
            import time
            epoch_timestamp = int(time.time())
            reset_command = f"R{epoch_timestamp}".encode()
            self.send_data(reset_command)
            print(f"Sent reset command with timestamp: R{epoch_timestamp}")
            
            # Start the reading thread
            self.stop_thread = False
            self.read_thread = threading.Thread(target=self._read_data_loop)
            self.read_thread.daemon = True
            self.read_thread.start()
            
            return True
        except serial.SerialException as e:
            print(f"Error connecting to port {port}: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self) -> bool:
        """
        Disconnect from the current serial port.
        
        Returns:
            True if disconnection was successful, False otherwise
        """
        if not self.is_connected:
            return True
            
        # Stop the reading thread
        self.stop_thread = True
        if self.read_thread:
            self.read_thread.join(timeout=1.0)
            self.read_thread = None
            
        # Close the serial connection
        if self.serial_connection:
            try:
                self.serial_connection.close()
                self.is_connected = False
                self.serial_connection = None
                return True
            except serial.SerialException as e:
                print(f"Error disconnecting: {e}")
                return False
        
        return True
    
    def set_data_callback(self, callback: Callable[[bytes], None]) -> None:
        """
        Set a callback function that will be called when data is received.
        
        Args:
            callback: Function that takes bytes and processes them
        """
        self.data_callback = callback
    
    def _read_data_loop(self) -> None:
        """
        Background thread that continuously reads data from the serial port
        and passes it to the callback function if set.
        """
        while not self.stop_thread and self.serial_connection:
            try:
                if self.serial_connection.in_waiting > 0:
                    data = self.serial_connection.read(self.serial_connection.in_waiting)
                    if data and self.data_callback:
                        self.data_callback(data)
                else:
                    time.sleep(0.01)  # Short sleep to prevent high CPU usage
            except serial.SerialException:
                self.stop_thread = True
                self.is_connected = False
                print("Serial connection lost")
                break
    
    def send_data(self, data: bytes) -> bool:
        """
        Send data to the connected serial port.
        Ensures message is terminated with a single newline character ('\n').
        
        Args:
            data: Bytes to send
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected or not self.serial_connection:
            return False
            
        try:
            # Ensure data ends with a single newline character
            if isinstance(data, bytes):
                # Strip any existing newline or carriage return characters
                data = data.rstrip(b'\r\n')
                # Append a single newline character
                data = data + b'\n'
            else:
                # Handle string case (though this should not typically occur)
                data = str(data).rstrip('\r\n') + '\n'
                data = data.encode()
                
            self.serial_connection.write(data)
            return True
        except serial.SerialException as e:
            print(f"Error sending data: {e}")
            return False
            
    def __del__(self):
        """Clean up resources when the object is destroyed."""
        self.disconnect()
