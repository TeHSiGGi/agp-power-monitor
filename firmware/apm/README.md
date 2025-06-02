# AGP Power Monitor Firmware

This firmware runs on an STM32 microcontroller to monitor power consumption of an AGP graphics card and associated power rails.

## Overview

The AGP Power Monitor provides accurate measurement of voltage and current across multiple power rails:
- AGP slot power (3.3V, 5V, 12V)
- External power connectors (4-pin, 6-pin)
- Alternative power channels

Data is collected at high frequency, processed, and streamed over USB serial connection for analysis.

## Hardware

- **Microcontroller**: STM32F103C8T6
- **Power Measurement**: Three INA3221 triple-channel power monitors
- **Status Indicators**: Two LEDs for operational status
- **Real-Time Clock**: Internal STM32 RTC for precise timestamping

### Monitored Power Rails

1. **INA3221 #1 (0x43)**:
   - Channel 1: Alternative channel A
   - Channel 2: Alternative channel B
   - Channel 3: 12V AGP

2. **INA3221 #2 (0x42)**:
   - Channel 1: 3.3V AGP
   - Channel 2: 5V AGP
   - Channel 3: VDDQ AGP

3. **INA3221 #3 (0x40)**:
   - Channel 1: 12V 6-pin connector
   - Channel 2: 5V 4-pin connector
   - Channel 3: 12V 4-pin connector

## Setup and Installation

### Prerequisites

- [PlatformIO](https://platformio.org/) (with VSCode or CLI)
- USB connection to the device
- STLink programmer

### Building and Flashing

1. Clone this repository
2. Open the project folder in VSCode with PlatformIO extension installed
3. Connect the STM32 board via USB and STLink
4. Build and upload using platform.io

## Serial Command Interface

Connect to the device using a serial monitor at 115200 baud (although baud rate doesn't matter over USB CDC).

### Available Commands

- **Set RTC**: `R<unix_timestamp>`  
  Sets the real-time clock with a Unix timestamp.
  Example: `R1658358000` (sets RTC to July 21, 2022 00:00:00 UTC)

- **Start Sampling**: `S`  
  Begins continuous power sampling and data output.
  Note: Requires RTC to be configured first.

- **Stop Sampling**: `P`  
  Stops the power sampling.

## Status LED Indicators

- **STAT_A LED**: Blinks when RTC is not configured, solid ON when RTC is set
- **STAT_B LED**: Toggles with each sampling cycle to indicate activity

## Data Output Format

When sampling, data is output continuously in binary format:

| Bytes | Description |
|-------|-------------|
| 0-3   | Unix timestamp (32-bit, big-endian) |
| 4     | Sample count (0-255 for each second) |
| 5-40  | Bus voltage readings (9 × 16-bit values) |
| 41-76 | Shunt voltage readings (9 × 16-bit values) |
| 77-78 | CRC-16 (CCITT) checksum |
| 79-81 | Packet end marker (FF0033) |

The values for the voltages are direct register values from the INA3221.

### Converting Values

- **Bus Voltage**: Raw value × LSB (0.008V)
- **Shunt Voltage**: Raw value × LSB (0.00004V)
- **Current**: Shunt voltage ÷ shunt resistor value

## Troubleshooting

- **No data output**: Ensure RTC is configured and sampling is started
- **Incorrect readings**: Check connections on INA3221 chips

## Disclaimer

This project is provided as is. There is no support or warranty on any parts of it (this includes hardware design, firmware and software). Use it at your own risk.

The author will not be accountable for any damage or harm inflicted.