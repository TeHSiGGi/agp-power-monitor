# AGP Power Monitor

The APM is a monitoring tool to determine the exact power consumption of an AGP Graphics Card.
It measures both power provided by the AGP slot as well as through external power sources via: 

- 6 pin Mini-Fit Jr. from Molex (PCIe Power) 
- 4 Pin AMP Mate-n-Lok 1-480424-0 (mostly known as Molex connector, though it isn't one).

## Hardware

At the heart of APM is a custom AGP Riser card which consists mainly of an STM32F103C8T6 and three INA3221 power monitors. 

It measures the voltages and currents of the AGP slot as well as of external power providers. Additionally there are two alternative inputs which can be used to measure any user-chosen external power rail as long as it is withing specification.

### Power Rails

The following power rails are being measured by the APM.

| Interface | Rail |
| -- | -- |
| AGP slot | 12V |
| AGP slot | 5V |
| AGP slot | 3.3V |
| AGP slot | VDDQ |
| External power | 12V (6Pin) |
| External power | 12V (4Pin) |
| External power | 5V (4Pin) |
| Alternative input | A |
| Alternative input | B |

### Resolution and limits

Each rail can measure:

- Up to 26V of voltage at 8mV steps
- Up to 10A of current at 4mA steps

These resolution values have to be take with a grain of salt, since these are theoretical numbers. The 26V and 10A are the absolute maximum ratings and must not be exceeded at any time.

### Connections:

- 2 keyed AGP gold finger connector
- Universal AGP slot
- Mini-Fit Jr 6 Pin input and output
- Mate-n-Lok 4 Pin input and output
- 2 Screw terminals for alternative channels A and B
- 4 Pin header for additional I2C devices
- 4 Pin header for STlink programming
- USB Mini B interface for connecting to a PC running the monitoring software

## Firmware

The APM uses an STM32F103C8T6 as its main processor. It serves as a USB interface providing fast access to the data provided by the INA3221.

The firmware is built using Platform.io and programmed via the 4 pin header on the board using STlink.

## Software

The monitoring software for APM is written in python and provides the following capabilities:

- Real time monitoring of all power rails (voltage, current, power)
- Automated calculation of minimum, maximum and average values over time of measurement
- Automated calculation of overall power per interface (AGP slot, external power and alternative inputs)
- Automated calculation of total power of all interfaces combined
  
## Known issues

- The layout of the AGP gold-fingers is a bit offset in the second and third segment
- CRC checking in the python application not implemented

## Wishlist for the future

- Plotting

## Reference values

To see some values from measured graphics cards, see [reference values](https://tehsiggi.github.io/agp-power-monitor/)

## Disclaimer

This project is provided as is. There is no support or warranty on any parts of it (this includes hardware design, firmware and software). Use it at your own risk.

The author will not be accountable for any damage or harm inflicted.