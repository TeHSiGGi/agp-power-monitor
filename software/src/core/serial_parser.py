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

import struct
import time
from typing import List, Dict, Optional, Union

class SerialDataParser:
    """
    Parser for serial data with the following package structure:
    - Epoch timestamp: 32-bit unsigned integer (UNIX time)
    - Sample in current time: 8-bit unsigned integer (0-255)
    - Bus voltages: 9 x 16-bit unsigned integers (raw values in mV)
    - Shunt currents: 9 x 16-bit signed integers (raw values in mA)
    - CRC-16 (CCITT): 16-bit checksum for data validation
    - FF0033: 3-byte end marker
    
    The parser detects packages by identifying the end marker of the previous package.
    """
    
    # Constants
    END_MARKER = b'\xFF\x00\x33'  # FF0033 in bytes
    PACKAGE_SIZE = 4 + 1 + 9*2 + 9*2 + 2 + 3  # timestamp + sample + voltages + currents + CRC + end marker
    
    def __init__(self):
        """Initialize the parser"""
        self.buffer = bytearray()
        # Note: incomplete_package variable was removed as it's not used
        self.last_package_time = 0
    
    # Note: _calculate_crc16_ccitt method was removed as it's not being used for validation
    
    def _validate_package(self, package: bytes) -> bool:
        """
        Validate a package (CRC check bypassed for now)
        
        Args:
            package: Complete package without the end marker
            
        Returns:
            True if package has sufficient length, False otherwise
        """
        
        # Check if package length matches expected size
        if len(package) != (self.PACKAGE_SIZE -3):  # Exclude end marker
            print(f"Invalid package size: {len(package)} bytes, expected {self.PACKAGE_SIZE} bytes")
            return False
        
        # Calculate CRC, remove the last 2 bytes (CRC)
        # crc = self._calculate_crc16_ccitt(package[:-2])
        # # Extract the CRC from the package (last 2 bytes before end marker)
        # package_crc = struct.unpack('>H', package[-5:-3])[0]  # Big-endian unsigned short
        # print (f"Calculated CRC: {crc}, Package CRC: {package_crc}")
    
        
        # Always return True, ignoring CRC check
        return True
        
    def parse_data(self, new_data: bytes) -> List[Dict[str, Union[int, List[int]]]]:
        """
        Process incoming data and extract complete packages
        
        Args:
            new_data: New data received from serial port
            
        Returns:
            List of parsed packages, each as a dictionary containing:
                - timestamp: Epoch time from the package
                - sample_id: Sample identifier in current time
                - voltages: List of 9 voltage values as 16-bit unsigned integers (raw values in mV)
                - currents: List of 9 shunt voltage values as 16-bit signed integers (raw values in uA)
        """
        # Add new data to buffer
        self.buffer.extend(new_data)
        result = []
        
        # Look for end markers to identify packages
        while True:
            marker_pos = self.buffer.find(self.END_MARKER)
            if marker_pos == -1:
                # No complete package in buffer
                break
                
            # We found an end marker, extract the package before it
            if marker_pos >= self.PACKAGE_SIZE - 3:  # Ensure there's enough data for a complete package
                package = self.buffer[:marker_pos]
                
                # Validate the package (only size check, CRC disabled)
                if self._validate_package(package):
                    # Parse the package
                    parsed = self._parse_package(package)
                    if parsed:
                        result.append(parsed)
                        
                        # Update last package time for tracking
                        self.last_package_time = time.time()
                
            # Remove the processed data and end marker from buffer
            self.buffer = self.buffer[marker_pos + len(self.END_MARKER):]
        
        # If buffer gets too large without finding end markers, clear it to prevent memory issues
        if len(self.buffer) > 10000:  # Arbitrary large size threshold
            print("Warning: Serial buffer getting too large without valid packages. Clearing buffer.")
            self.buffer.clear()
            
        return result
    
    def _parse_package(self, package: bytes) -> Optional[Dict[str, Union[int, List[int]]]]:
        """
        Parse a single package from raw bytes
        
        Args:
            package: Complete package bytes (without end marker)
            
        Returns:
            Dictionary with parsed values or None if parsing failed
        """
        try:
            # Extract timestamp (4 bytes)
            timestamp = struct.unpack('>I', package[0:4])[0]
            
            # Extract sample ID (1 byte)
            sample_id = package[4]
            
            # Extract voltages (9 x 2 bytes, unsigned)
            voltages = []
            for i in range(9):
                offset = 5 + (i * 2)
                # Get the two bytes for voltage, big-endian unsigned short
                voltage_mV = struct.unpack('>H', package[offset:offset+2])[0]  # Big-endian unsigned short
                # We can directly use the voltage in mV, as the first three bits are always 0, which means we already
                # have 8mV resolution and can simply use the value as signed 16-bit integer
                voltages.append(voltage_mV)
            
            # Extract currents (9 x 2 bytes, signed)
            currents = []
            for i in range(9):
                offset = 5 + 9*2 + (i * 2)
                shunt_voltage = struct.unpack('>h', package[offset:offset+2])[0]  # Big-endian signed short
                # The first three bits are always 0, means the value is incremented in steps of 8,
                # A step of 8 corresponds to 40µV, so we will have to multiply the value by 5 to get the actual shunt voltage in µV
                shunt_voltage *= 5  # Convert to µV
                # We can divide shunt voltage by the shunt resistor value in mOhm to get the current in mA
                current_raw = shunt_voltage // 10  # Assuming a shunt resistor of 10 mOhm
                currents.append(current_raw)  # Raw value in mA
            
            return {
                'timestamp': timestamp,
                'sample_id': sample_id, 
                'voltages': voltages,
                'currents': currents
            }
            
        except Exception as e:
            print(f"Error parsing package: {e}")
            return None
    
    # Note: get_data_rate method was removed as it's not being used in the codebase.
