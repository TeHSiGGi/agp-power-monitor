# AGP Power Monitor Hardware

## Project Overview

The AGP Power Monitor is uses a custom AGP riser card to measure and monitor power consumption of AGP cards. It provides real-time voltage and current measurements for the various power rails used by AGP graphics cards, allowing for detailed power analysis and troubleshooting.

## Hardware Design

### Main Components

- **AGP Connectors**: Edge connector for AGP cards and slot connector for motherboard interface
- **Power Measurement**: INA3221 triple-channel power monitors for measuring voltage and current
- **Microcontroller**: STM32F103C8T6 MCU for data processing and USB communication
- **Power Supply**: All logic is powered via the USB input
- **USB Interface**: USB connectivity for data output and device control

### Design Notes

The PCB is a multi-layer design featuring:
- 4 layer with dedicated ground and power planes
- length matches AGP data lines

The USB input is using a polyfuse to prevent damage in case of shortcuts. The 3.3V output of the onboard regulator must not be loaded with more than 250mA. 

You can use the I2C header to connect additional hardware if needed.

The board features pin headers on the backside that can be used for calibration and rail measurement with external measurement equipment.

### Key Features

1. **Inline Power Measurement**: Non-intrusive monitoring between motherboard and graphics card
2. **Multiple Rail Monitoring**: Simultaneous monitoring of AGP power rails (3.3V, 5V, 12V, VDDQ)
3. **External Power Input**: Additional power connectors for supplementary power testing
4. **I²C Expansion**: I²C interface for connecting additional sensors or displays
5. **USB Interface**: Data logging and real-time monitoring via USB

## Connectors and Interfaces

| Connector | Description | Function |
|-----------|-------------|----------|
| J201 | AGP Edge Connector | Connects to motherboard AGP slot |
| J202 | AGP Slot Connector | Receives AGP graphics card |
| J301/J302 | External Power | 6Pin External 12V power input connectors |
| J303/J304 | External Power | 4Pin 5V/12V power output connector |
| J305/J306 | Alternative Power | Alternative power measurement points |
| J501 | USB Connector | USB data interface |
| J502 | I²C Header | External I²C device connection |

## KiCad Files and Libraries

This project is designed using KiCad 9.0. The directory includes:

- `apm.kicad_pro` - KiCad project file
- `apm.kicad_sch` - Main schematic file
- `apm.kicad_pcb` - PCB layout file
- `lib/` - Custom component libraries:
  - AGP edge connector footprints and symbols
  - AGP slot connector footprints and symbols
  - Power connector footprints and symbols

### Schematic Organization

The schematic is organized into multiple sheets for clarity:

1. **Main Sheet**: Overall system connections
2. **AGP Connectors**: AGP interface connections
3. **External Power**: Power input and conditioning circuits
4. **Sensors**: Power measurement circuits using INA3221
5. **USB Interface**: STM32 microcontroller and USB interface

## Setup Instructions

### Assembly Notes

1. The board requires SMD soldering capabilities (down to 0603 components, QFN packages)
2. Pay special attention to the alignment of AGP connectors
3. The PCB is designed for standard 1.6mm thickness
4. Edge plating is required for the AGP edge connector
5. Beveling (20°) is used during manufacturing

The PCBs have successfully been manufactured at pcbway.com

## BOM

| Part Type | Value/Model | Footprint | Qty | Comment |
|-----------|-------------|-----------|-----|---------|
| Capacitors | 4µ7 | 1206 | 2 | Bulk capacitors for 12V rail |
| | 22µ | 1206 | 12 | Bulk capacitors for 3.3V, 5V and VDDQ rail, USB Bus power |
| | 1µ | 0603 | 10 | Bypass capacitors for external and alternative inputs |
| | 100n | 0603 | 16 | Bypass capacitors and filter capacitors for INA3221|
| | 10µ | 1206 | 1 | Bypass capacitor for 3.3V from USB power |
| | 20p | 0603 | 4 | Crystal load capacitors |
| | 10n | 0603 | 1 | Capacitor for reset circuit |
| Resistors | 0R01 | 2816 | 9 | Current shunt resistors |
| | 10 | 0603 | 18 | Pull-up/pull-down resistors |
| | 22 | 0603 | 2 | USB termination resistors |
| | 1M | 0603 | 1 | Crystal load resistor |
| | 10k | 0603 | 1 | Pull-up resistor |
| | 4k7 | 0603 | 1 | Pull-up resistor |
| | 3k3 | 0603 | 3 | Pull-up resistors |
| | 220 | 0603 | 3 | LED current limiting resistors |
| ICs | INA3221 | VQFN | 3 | Triple-channel power monitor |
| | MCP1703AT3302ECB | SOT-23 | 1 | 3.3V voltage regulator |
| | STM32F103C8T6 | LQFP-48 | 1 | 32-bit ARM microcontroller |
| Protection | PRTR5V0U2X | SOT-143 | 2 | USB ESD protection |
| | P4SMAJ5.0A | SMA | 1 | TVS diode |
| | 200mA | 1812 | 1 | Polyfuse |
| Connectors | AGP Edge Connector | edge_universal | 1 | Motherboard interface |
| | 145376-2 | 145376-2 AMP | 1 | AGP card slot |
| | 12V/3.3V/VDDQ/5V/GND PROBE | Pin Header 2 Pin 2.54mm | 10 | Test points |
| | 39301060 | Molex_Mini-Fit_Jr_5569-06A2_2x03_P4.20mm_Horizontal | 2 | 6-pin power connectors |
| | 641737-1 | 641737-1 | 2 | 4-pin power connectors |
| | Screw_Terminal_01x02 | 5.08mm Horizontal | 2 | Alternative power input |
| | USB_B_Mini | Wuerth 65100516121 | 1 | USB interface |
| | I2C/STLink Headers | PinHeader 4 Pin 2.54mm | 2 | Expansion/Programming headers |
| Indicators | LED | 1206 | 3 | Status indicators |
| Crystals | 8MHz | HC49l | 1 | Main MCU oscillator |
| | 32.768kHz | DS10 | 1 | RTC oscillator |

## Revision History

- Rev 1.0.0: Initial hardware design

## Disclaimer

This project is provided as is. There is no support or warranty on any parts of it (this includes hardware design, firmware and software). Use it at your own risk.

The author will not be accountable for any damage or harm inflicted.