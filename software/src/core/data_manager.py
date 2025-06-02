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

import csv
from collections import deque
import time
import sys
from typing import Dict, List, Any

class DataManager:
    """
    Buffer manager for rail voltage, current and power data.
    Maintains statistics (average, min, max) for all values.
    Also manages connection and sampling status.
    """
    
    def __init__(self, max_buffer_size_mb: float = 100.0, config_manager=None):
        """
        Initialize the data manager with a configurable buffer size.
        
        Args:
            max_buffer_size_mb: Maximum buffer size in megabytes
            config_manager: Optional ConfigManager instance for centralized settings
        """
        self.NUM_RAILS = 9
        self.config_manager = config_manager
        
        # Get buffer size from config manager if available
        if config_manager:
            max_buffer_size_mb = config_manager.get("measurement.maxBufferSizeMB", max_buffer_size_mb)
            # Register callback for buffer size changes
            config_manager.register_callback("measurement.maxBufferSizeMB", self._on_buffer_size_changed)
            
        self.max_buffer_size_bytes = int(max_buffer_size_mb * 1024 * 1024)
        self.data_buffer = deque()
        
        # Connection and sampling state
        self.is_connected = False
        self.is_sampling = False
        
        # Tracking insert rate
        self.insert_times = deque(maxlen=1000)  # Track last 1000 inserts for rate calculation
        
        # Statistics for each rail
        self.stats = {
            'voltage': {'avg': [0] * self.NUM_RAILS, 'min': [float('inf')] * self.NUM_RAILS, 'max': [float('-inf')] * self.NUM_RAILS},
            'current': {'avg': [0] * self.NUM_RAILS, 'min': [float('inf')] * self.NUM_RAILS, 'max': [float('-inf')] * self.NUM_RAILS},
            'power': {'avg': [0] * self.NUM_RAILS, 'min': [float('inf')] * self.NUM_RAILS, 'max': [float('-inf')] * self.NUM_RAILS}
        }
        
        # Running sums for average calculation
        self._sums = {
            'voltage': [0] * self.NUM_RAILS,
            'current': [0] * self.NUM_RAILS,
            'power': [0] * self.NUM_RAILS
        }
        self.total_entries = 0
    
    def get_buffer_size_bytes(self) -> int:
        """Get the current buffer size in bytes"""
        # Estimate size of the buffer using sys.getsizeof
        return sum(sys.getsizeof(item) for item in self.data_buffer)
    
    def get_buffer_size_mb(self) -> float:
        """Get the current buffer size in megabytes"""
        return self.get_buffer_size_bytes() / (1024 * 1024)
    
    def get_max_buffer_size_mb(self) -> float:
        """Get the maximum buffer size in megabytes"""
        return self.max_buffer_size_bytes / (1024 * 1024)
    
    def set_max_buffer_size_mb(self, max_buffer_size_mb: float) -> None:
        """Set the maximum buffer size in megabytes"""
        self.max_buffer_size_bytes = int(max_buffer_size_mb * 1024 * 1024)
        # Trim buffer if needed
        self._trim_buffer_if_needed()
        
        # Update setting in config manager if available
        if self.config_manager:
            # This will avoid recursion since we don't update max_buffer_size_bytes 
            # if it's the same value
            self.config_manager.set("measurement.maxBufferSizeMB", max_buffer_size_mb)
            
    def _on_buffer_size_changed(self, key, new_value, old_value):
        """
        Callback for when buffer size setting changes in config manager
        
        Args:
            key: The setting key (always "measurement.maxBufferSizeMB")
            new_value: New buffer size in MB
            old_value: Previous buffer size in MB
        """
        if new_value != old_value:
            # Update buffer size in bytes
            self.max_buffer_size_bytes = int(new_value * 1024 * 1024)
            # Trim buffer if needed
            self._trim_buffer_if_needed()
    
    def _trim_buffer_if_needed(self) -> None:
        """Remove oldest entries if buffer exceeds max size"""
        current_size = self.get_buffer_size_bytes()
        while current_size > self.max_buffer_size_bytes and self.data_buffer:
            # Remove oldest entry
            removed_entry = self.data_buffer.popleft()
            
            # Update statistics when removing entries
            if self.total_entries > 0:
                self.total_entries -= 1
                
                # Update sums for removed entry
                for rail_idx in range(self.NUM_RAILS):
                    self._sums['voltage'][rail_idx] -= removed_entry['voltage'][rail_idx]
                    self._sums['current'][rail_idx] -= removed_entry['current'][rail_idx]
                    self._sums['power'][rail_idx] -= removed_entry['power'][rail_idx]
                
                # Recalculate averages if we still have data
                if self.total_entries > 0:
                    self._recalculate_stats()
                else:
                    # Reset stats if buffer is empty
                    self._reset_stats()
            
            current_size = self.get_buffer_size_bytes()
    
    def _reset_stats(self) -> None:
        """Reset statistics when buffer is empty"""
        for metric in ['voltage', 'current', 'power']:
            self.stats[metric]['avg'] = [0] * self.NUM_RAILS
            self.stats[metric]['min'] = [float('inf')] * self.NUM_RAILS
            self.stats[metric]['max'] = [float('-inf')] * self.NUM_RAILS
            self._sums[metric] = [0] * self.NUM_RAILS
    
    def _recalculate_stats(self) -> None:
        """Recalculate min, max values by scanning the entire buffer"""
        # This is called when entries are removed and we need to ensure min/max are accurate
        if not self.data_buffer:
            self._reset_stats()
            return
            
        # Reset min/max
        for metric in ['voltage', 'current', 'power']:
            self.stats[metric]['min'] = [float('inf')] * self.NUM_RAILS
            self.stats[metric]['max'] = [float('-inf')] * self.NUM_RAILS
        
        # Scan buffer for new min/max
        for entry in self.data_buffer:
            for rail_idx in range(self.NUM_RAILS):
                for metric in ['voltage', 'current', 'power']:
                    value = entry[metric][rail_idx]
                    self.stats[metric]['min'][rail_idx] = min(self.stats[metric]['min'][rail_idx], value)
                    self.stats[metric]['max'][rail_idx] = max(self.stats[metric]['max'][rail_idx], value)
        
        # Update averages
        for metric in ['voltage', 'current', 'power']:
            for rail_idx in range(self.NUM_RAILS):
                self.stats[metric]['avg'][rail_idx] = self._sums[metric][rail_idx] / self.total_entries if self.total_entries > 0 else 0
    
    def insert_data(self, voltages: List[float], currents: List[float]) -> None:
        """
        Insert a new data packet containing voltage and current values for all rails.
        
        Args:
            voltages: List of voltage values for each rail (9 values)
            currents: List of current values for each rail (9 values)
        """
        if len(voltages) != self.NUM_RAILS or len(currents) != self.NUM_RAILS:
            raise ValueError(f"Expected {self.NUM_RAILS} values for both voltage and current")
        
        # Calculate power for each rail
        powers = [v * c for v, c in zip(voltages, currents)]
        
        # Create timestamp
        timestamp = time.time()
        self.insert_times.append(timestamp)
        
        # Create data entry
        entry = {
            'timestamp': timestamp,
            'voltage': voltages.copy(),
            'current': currents.copy(),
            'power': powers
        }
        
        # Add to buffer
        self.data_buffer.append(entry)
        self.total_entries += 1
        
        # Update stats
        for rail_idx in range(self.NUM_RAILS):
            # Update sums for average calculation
            self._sums['voltage'][rail_idx] += voltages[rail_idx]
            self._sums['current'][rail_idx] += currents[rail_idx]
            self._sums['power'][rail_idx] += powers[rail_idx]
            
            # Update averages
            for metric, values in zip(['voltage', 'current', 'power'], [voltages, currents, powers]):
                value = values[rail_idx]
                self.stats[metric]['avg'][rail_idx] = self._sums[metric][rail_idx] / self.total_entries
                self.stats[metric]['min'][rail_idx] = min(self.stats[metric]['min'][rail_idx], value)
                self.stats[metric]['max'][rail_idx] = max(self.stats[metric]['max'][rail_idx], value)
        
        # Check if we need to trim the buffer
        self._trim_buffer_if_needed()
    
    def get_data(self) -> List[Dict[str, Any]]:
        """Get all data points in the buffer"""
        return list(self.data_buffer)
    
    # Note: get_data_since_timestamp method was removed as it's not being used in the codebase.
    
    def get_rail_stats(self, rail_idx: int) -> Dict[str, Dict[str, float]]:
        """
        Get statistics for a specific rail
        
        Args:
            rail_idx: Index of the rail (0-8)
            
        Returns:
            Dictionary with stats for voltage, current and power
        """
        if not 0 <= rail_idx < self.NUM_RAILS:
            raise ValueError(f"Rail index must be between 0 and {self.NUM_RAILS-1}")
        
        result = {}
        for metric in ['voltage', 'current', 'power']:
            result[metric] = {
                'avg': self.stats[metric]['avg'][rail_idx],
                'min': self.stats[metric]['min'][rail_idx] if self.stats[metric]['min'][rail_idx] != float('inf') else 0,
                'max': self.stats[metric]['max'][rail_idx] if self.stats[metric]['max'][rail_idx] != float('-inf') else 0
            }
        
        return result
    
    def get_all_stats(self) -> Dict[str, Dict[str, List[float]]]:
        """Get statistics for all rails"""
        return {
            'voltage': {
                'avg': self.stats['voltage']['avg'],
                'min': [v if v != float('inf') else 0 for v in self.stats['voltage']['min']],
                'max': [v if v != float('-inf') else 0 for v in self.stats['voltage']['max']]
            },
            'current': {
                'avg': self.stats['current']['avg'],
                'min': [v if v != float('inf') else 0 for v in self.stats['current']['min']],
                'max': [v if v != float('-inf') else 0 for v in self.stats['current']['max']]
            },
            'power': {
                'avg': self.stats['power']['avg'],
                'min': [v if v != float('inf') else 0 for v in self.stats['power']['min']],
                'max': [v if v != float('-inf') else 0 for v in self.stats['power']['max']]
            }
        }
    
    def get_current_buffer_entries(self) -> int:
        """Get number of entries currently in the buffer"""
        return len(self.data_buffer)
    
    def get_packets_per_second(self) -> float:
        """Calculate the number of data packets being inserted per second"""
        if len(self.insert_times) < 2:
            return 0.0
        
        # Calculate time difference between oldest and newest insert
        time_diff = self.insert_times[-1] - self.insert_times[0]
        if time_diff <= 0:
            return 0.0
            
        # Calculate packets per second
        return (len(self.insert_times) - 1) / time_diff
    
    def clear_buffer(self) -> None:
        """Clear all data in the buffer"""
        self.data_buffer.clear()
        self.insert_times.clear()
        self.total_entries = 0
        self._reset_stats()
        
    # Connection state management
    def set_connected(self, is_connected: bool) -> None:
        """
        Set the connection state. If disconnecting and currently sampling, 
        automatically stops sampling.
        
        Args:
            is_connected (bool): True if connected, False if disconnected
        """
        previous_state = self.is_connected
        self.is_connected = is_connected
        
        # If disconnecting and currently sampling, stop sampling
        if previous_state and not is_connected and self.is_sampling:
            self.set_sampling(False)
            
    def get_connected(self) -> bool:
        """
        Get the current connection state
        
        Returns:
            bool: True if connected, False if disconnected
        """
        return self.is_connected
        
    # Sampling state management
    def set_sampling(self, is_sampling: bool) -> bool:
        """
        Set the sampling state. Sampling requires connection.
        
        Args:
            is_sampling (bool): True to start sampling, False to stop sampling
            
        Returns:
            bool: True if the state was changed, False if not (e.g. can't start sampling when disconnected)
        """
        # Can't start sampling if not connected
        if is_sampling and not self.is_connected:
            return False
            
        self.is_sampling = is_sampling
        return True
        
    def get_sampling(self) -> bool:
        """
        Get the current sampling state
        
        Returns:
            bool: True if sampling, False if not sampling
        """
        return self.is_sampling
    
    def export_to_csv(self, filepath: str) -> bool:
        """
        Export all data in the buffer to a CSV file.
        
        Args:
            filepath (str): Path to the CSV file to create
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        if not self.data_buffer:
            return False
        
        try:
            with open(filepath, 'w', newline='') as csvfile:
                # Define CSV headers
                fieldnames = [
                    'timestamp', 'datetime',  # Time fields
                    # Voltage fields for all rails
                    'voltage_input_a', 'voltage_input_b', 
                    'voltage_12v', 'voltage_vddq', 'voltage_5v', 'voltage_3.3v',
                    'voltage_12v_6pin', 'voltage_12v_4pin', 'voltage_5v_4pin',
                    # Current fields for all rails
                    'current_input_a', 'current_input_b',
                    'current_12v', 'current_vddq', 'current_5v', 'current_3.3v',
                    'current_12v_6pin', 'current_12v_4pin', 'current_5v_4pin',
                    # Power fields for all rails
                    'power_input_a', 'power_input_b',
                    'power_12v', 'power_vddq', 'power_5v', 'power_3.3v',
                    'power_12v_6pin', 'power_12v_4pin', 'power_5v_4pin',
                    # Total power
                    'power_total'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # Write all data entries
                for entry in self.data_buffer:
                    # Convert timestamp to human readable format
                    timestamp = entry['timestamp']
                    datetime_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
                    
                    # Calculate total power
                    total_power = sum([v * c for v, c in zip(entry['voltage'], entry['current'])])
                    
                    # Prepare row data
                    row = {
                        'timestamp': timestamp,
                        'datetime': datetime_str
                    }
                    
                    # Rail names mapping to ensure consistent order in CSV
                    rail_indices = [0, 1, 2, 3, 4, 5, 6, 7, 8]  # 0-8 for 9 rails
                    
                    # Add voltage data
                    for i, idx in enumerate(rail_indices):
                        if i == 0:
                            prefix = 'input_a'
                        elif i == 1:
                            prefix = 'input_b'
                        elif i == 2:
                            prefix = '12v'
                        elif i == 3:
                            prefix = 'vddq'
                        elif i == 4:
                            prefix = '5v'
                        elif i == 5:
                            prefix = '3.3v'
                        elif i == 6:
                            prefix = '12v_6pin'
                        elif i == 7:
                            prefix = '12v_4pin'
                        elif i == 8:
                            prefix = '5v_4pin'
                            
                        row[f'voltage_{prefix}'] = entry['voltage'][idx]
                        row[f'current_{prefix}'] = entry['current'][idx]
                        row[f'power_{prefix}'] = entry['voltage'][idx] * entry['current'][idx]
                    
                    # Add total power
                    row['power_total'] = total_power
                    
                    # Write the row
                    writer.writerow(row)
                    
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
