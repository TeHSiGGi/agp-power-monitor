# AGP Power Monitor

A Qt-based Python application with a tabbed interface designed for monitoring power.

## Features

- Real time data display of all rails
- Average, Maximum and Minimum calculation
- Export of data into CSV
- Copy of power statistics as markdown

## Setup and starting

Use the `setup.sh` shell script:

`setup.sh install` to install all required libraries.

`setup.sh start` to start the application

`setup.sh start /dev/ttyACM0` adds the serial interface to be used

## Configuration

You can either modify the `config.yaml` file to meet your setup or provide overrides when running the program.

Allowed flags are:
- `port` - Serial port to connect to (e.g., `/dev/ttyACM0`, `COM3`)
- `--correction-factor` or `-c` - Current correction factor
- `--debug` or `-d` - Enable debug output
- `--baudrate` or `-b` - Serial baudrate
- `--config` - Path to a custom config.yaml file

Example:
```
./setup.sh start /dev/ttyUSB0 --debug --baudrate 9600
```

## Configuration File Structure

The `config.yaml` file contains the following sections:

```yaml
serial:
  port: /dev/ttyACM0      # Serial port to connect to
  baudrate: 115200        # Serial port baudrate
  timeout: 1.0            # Read timeout in seconds

measurement:
  uiUpdateInterval: 100   # Update interval for UI values in milliseconds
  currentCorrectionFactor: 1.0275  # Factor to adjust current readings
  maxBufferSizeMB: 100.0  # Maximum buffer size in megabytes

debugLog: false           # Enable/disable debug logging
```

## Serial Data Protocol

The application communicates with hardware devices using a custom serial protocol. Each data package contains:

- Epoch timestamp (32-bit unsigned integer)
- Sample ID in current time (8-bit unsigned integer)
- Bus voltages for 9 rails (16-bit unsigned integers, direct register values)
- Shunt voltages for 9 rails (16-bit signed integers, direct register values)
- CRC-16 (CCITT) checksum for data validation
- 3-byte end marker (FF0033)

## Disclaimer

This project is provided as is. There is no support or warranty on any parts of it (this includes hardware design, firmware and software). Use it at your own risk.

The author will not be accountable for any damage or harm inflicted.