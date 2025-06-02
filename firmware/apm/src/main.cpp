#include <Arduino.h>
#include <Wire.h>
#include <STM32RTC.h>

// LEDs for status indication
#define STAT_A_LED PA4
#define STAT_B_LED PA5

// INA3221 I2C addresses
// U401 - rails: alternative channel A and B, 12V AGP
#define INA1_ADDRESS 0x43
// U402 - rails: 3.3V AGP, 5V AGP, VDDQ AGP
#define INA2_ADDRESS 0x42
// U403 - rails: 12V 6Pin, 5V 4Pin, 12V 4Pin
#define INA3_ADDRESS 0x40

// INA3221 register addresses
#define INA3221_REG_CONFIG         0x00
#define INA3221_REG_SHUNTVOLTAGE_1 0x01
#define INA3221_REG_BUSVOLTAGE_1   0x02
// Each channel is +2 from previous
#define INA3221_REG_SHUNTVOLTAGE_2 0x03
#define INA3221_REG_BUSVOLTAGE_2   0x04
#define INA3221_REG_SHUNTVOLTAGE_3 0x05
#define INA3221_REG_BUSVOLTAGE_3   0x06

// Serial command definitions
#define CMD_SET_RTC      'R'  // Set RTC: R<unix_timestamp>
#define CMD_START_SAMPLE 'S'  // Start sampling: S
#define CMD_STOP_SAMPLE  'P'  // Stop sampling: P

// Sampling control
bool samplingActive = false;
bool rtcConfigured = false;
unsigned long lastBlinkTime = 0;
const unsigned long blinkInterval = 500;

// RTC object
STM32RTC& rtc = STM32RTC::getInstance();
time_t previousSampleTime = 0;
int8_t sampleCount = 0;

// Command buffer
const int MAX_CMD_LENGTH = 32;
char cmdBuffer[MAX_CMD_LENGTH];
int cmdIndex = 0;

// CRC-16 (CCITT) calculation function
uint16_t crc16_ccitt(const uint8_t* data, size_t length) {
  uint16_t crc = 0xFFFF;
  for (size_t i = 0; i < length; i++) {
    crc ^= (uint16_t)data[i] << 8;
    for (uint8_t j = 0; j < 8; j++) {
      if (crc & 0x8000) crc = (crc << 1) ^ 0x1021;
      else crc <<= 1;
    }
  }
  return crc;
}

// Helper to write 16-bit register to INA3221
void writeINA3221Register(uint8_t address, uint8_t reg, uint16_t value) {
  Wire.beginTransmission(address);
  Wire.write(reg);
  Wire.write((value >> 8) & 0xFF);
  Wire.write(value & 0xFF);
  Wire.endTransmission();
}

// Helper to read 16-bit register from INA3221
uint16_t readINA3221Register(uint8_t address, uint8_t reg) {
  Wire.beginTransmission(address);
  Wire.write(reg);
  Wire.endTransmission(false);
  Wire.requestFrom(address, (uint8_t)2);
  uint16_t value = 0;
  if (Wire.available() == 2) {
    value = (Wire.read() << 8) | Wire.read();
  }
  return value;
}

// Initialize INA3221
void setupINA3221() {
  // Continuous mode, enable all channels, averaging 16 samples, using 1.1ms conversion time for both shunt and bus voltages
  // 15   14   13   12   11   10   9    8    7    6    5    4    3    2    1    0
  // RST  EN1  EN2  EN3  AV2  AV1  AV0  CB2  CB1  CB0  CS2  CS1  CS0  M3   M2   M1
  // 1    1    1    1    0    1    0    1    0    0    1    0    0    1    1    1
  // This sets the INA3221 to: 0b1111010101000111
  // This sets the INA3221 to: 0xF547
  writeINA3221Register(INA1_ADDRESS, INA3221_REG_CONFIG, 0xF547);
  writeINA3221Register(INA2_ADDRESS, INA3221_REG_CONFIG, 0xF547);
  writeINA3221Register(INA3_ADDRESS, INA3221_REG_CONFIG, 0xF547);
}

// Update LED status based on RTC configuration
void updateStatusLED() {
  if (!rtcConfigured) {
    // Blink STAT_A_LED if RTC is not configured
    if (millis() - lastBlinkTime >= blinkInterval) {
      lastBlinkTime = millis();
      digitalWrite(STAT_A_LED, !digitalRead(STAT_A_LED));
    }
  } else {
    // Solid LED if RTC is configured
    digitalWrite(STAT_A_LED, HIGH);
  }
}

// Process and take a sample
void takeSample() {
  // Read the current time from the RTC
  time_t currentSampleTime = rtc.getEpoch();

  // Check if the time has changed since the last sample
  if (currentSampleTime != previousSampleTime) {
    // Reset the sample counter for the new seconds we're running in
    sampleCount = 0;
  } else {
    // Increment the sample count
    sampleCount++;
  }
  // Update the previous sample time
  previousSampleTime = currentSampleTime;

  // Create a data buffer to accommodate 16-bit values
  uint8_t data[50];
  
  // Timestamp - 4 bytes (32 bits)
  // Store the current sample time in big-endian format
  data[0] = (currentSampleTime >> 24) & 0xFF;
  data[1] = (currentSampleTime >> 16) & 0xFF;
  data[2] = (currentSampleTime >> 8) & 0xFF;
  data[3] = currentSampleTime & 0xFF;
  
  // Sample count - 1 byte
  data[4] = sampleCount;
  
  // Process bus voltages (convert to mV as 16-bit values)
  // Each value takes 2 bytes (16 bits)
  int index = 5;

  // Function to store a 16-bit value in the data array,
  // The data is a signed 16-bit
  // Storing the high byte first, then the low byte (big-endian format)
  auto store16BitValue = [&data, &index](uint16_t value) {
    data[index++] = (value >> 8) & 0xFF; // High byte
    data[index++] = value & 0xFF;        // Low byte
  };

  // Store all bus voltages
  store16BitValue(readINA3221Register(INA1_ADDRESS, INA3221_REG_BUSVOLTAGE_1)); // Channel 1
  store16BitValue(readINA3221Register(INA1_ADDRESS, INA3221_REG_BUSVOLTAGE_2)); // Channel 2
  store16BitValue(readINA3221Register(INA1_ADDRESS, INA3221_REG_BUSVOLTAGE_3)); // Channel 3
  store16BitValue(readINA3221Register(INA2_ADDRESS, INA3221_REG_BUSVOLTAGE_1)); // Channel 1
  store16BitValue(readINA3221Register(INA2_ADDRESS, INA3221_REG_BUSVOLTAGE_2)); // Channel 2
  store16BitValue(readINA3221Register(INA2_ADDRESS, INA3221_REG_BUSVOLTAGE_3)); // Channel 3
  store16BitValue(readINA3221Register(INA3_ADDRESS, INA3221_REG_BUSVOLTAGE_1)); // Channel 1
  store16BitValue(readINA3221Register(INA3_ADDRESS, INA3221_REG_BUSVOLTAGE_2)); // Channel 2
  store16BitValue(readINA3221Register(INA3_ADDRESS, INA3221_REG_BUSVOLTAGE_3)); // Channel 3

  // Store all currents
  store16BitValue(readINA3221Register(INA1_ADDRESS, INA3221_REG_SHUNTVOLTAGE_1)); // Channel 1
  store16BitValue(readINA3221Register(INA1_ADDRESS, INA3221_REG_SHUNTVOLTAGE_2)); // Channel 2
  store16BitValue(readINA3221Register(INA1_ADDRESS, INA3221_REG_SHUNTVOLTAGE_3)); // Channel 3
  store16BitValue(readINA3221Register(INA2_ADDRESS, INA3221_REG_SHUNTVOLTAGE_1)); // Channel 1
  store16BitValue(readINA3221Register(INA2_ADDRESS, INA3221_REG_SHUNTVOLTAGE_2)); // Channel 2
  store16BitValue(readINA3221Register(INA2_ADDRESS, INA3221_REG_SHUNTVOLTAGE_3)); // Channel 3
  store16BitValue(readINA3221Register(INA3_ADDRESS, INA3221_REG_SHUNTVOLTAGE_1)); // Channel 1
  store16BitValue(readINA3221Register(INA3_ADDRESS, INA3221_REG_SHUNTVOLTAGE_2)); // Channel 2
  store16BitValue(readINA3221Register(INA3_ADDRESS, INA3221_REG_SHUNTVOLTAGE_3)); // Channel 3

  // Calculate CRC-16 (CCITT) for the data packet
  uint16_t crc = crc16_ccitt(data, index);
  // Store the CRC-16 in the data packet
  data[index++] = (crc >> 8) & 0xFF; // High byte
  data[index++] = crc & 0xFF;        // Low byte

  // Add a FF0033 to the end of the data packet
  data[index++] = 0xFF;
  data[index++] = 0x00;
  data[index++] = 0x33;

  // Write the data to the serial port
  Serial.write(data, index);

  // Toggle the STAT_B_LED to indicate sampling activity
  if (sampleCount == 0) {
    digitalWrite(STAT_B_LED, !digitalRead(STAT_B_LED));
  }
}

// Process a complete command
void processCommand(char* cmd) {
  if (cmd[0] == CMD_SET_RTC) {
    // Only allow RTC setting if not currently sampling
    if (!samplingActive) {
      // Parse the timestamp from the command string
      time_t newTime = strtoul(&cmd[1], NULL, 10);
      if (newTime > 1609459200) { // Sanity check: after Jan 1, 2021
        rtc.setEpoch(newTime);
        rtcConfigured = true;
        Serial.println("RTC set");
      } else {
        Serial.println("Invalid timestamp");
      }
    } else {
      Serial.println("Stop sampling first");
    }
  } 
  else if (cmd[0] == CMD_START_SAMPLE) {
    if (rtcConfigured) {
      samplingActive = true;
      Serial.println("Sampling started");
    } else {
      Serial.println("Configure RTC first");
    }
  } 
  else if (cmd[0] == CMD_STOP_SAMPLE) {
    samplingActive = false;
    Serial.println("Sampling stopped");
  } 
}

// Process incoming serial data for commands
void handleSerial() {
  while (Serial.available() > 0) {
    char inChar = (char)Serial.read();
    
    // If newline or carriage return, process the command
    if (inChar == '\n' || inChar == '\r') {
      if (cmdIndex > 0) {
        cmdBuffer[cmdIndex] = '\0';
        processCommand(cmdBuffer);
        cmdIndex = 0;
      }
    } 
    // Otherwise add to buffer if not full
    else if (cmdIndex < MAX_CMD_LENGTH - 1) {
      cmdBuffer[cmdIndex++] = inChar;
    }
  }
}

void setup() {
  // Initialize serial communication, baud rate does not matter, since we're running over USB
  Serial.begin(115200);
  // Set the LED pins as outputs
  pinMode(STAT_A_LED, OUTPUT);
  pinMode(STAT_B_LED, OUTPUT);
  // Set the LED pins to LOW to turn them off
  digitalWrite(STAT_A_LED, LOW);
  digitalWrite(STAT_B_LED, LOW);

  // Initialize the I2C bus
  Wire.begin();
  // Set the I2C bus frequency to 400kHz
  Wire.setClock(400000);

  // Initialize the RTC
  rtc.begin(true, STM32RTC::HOUR_24);

  // Run initialization for INA3221
  setupINA3221();
}

void loop() {
  // Update the LED status based on RTC configuration
  updateStatusLED();
  
  // Handle incoming serial commands
  handleSerial();
  
  // If sampling is active, take a sample
  if (samplingActive && rtcConfigured) {
    takeSample();
  }
}