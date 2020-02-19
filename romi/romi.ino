#include <Servo.h>
#include <Romi32U4.h>
#include <PololuRPiSlave.h>
#include <Wire.h>
#include <LSM6.h>
#include "TurnSensor.h"

#define LEFT_SENSOR_PIN 0
#define CENTER_SENSOR_PIN 2
#define RIGHT_SENSOR_PIN 3

// Custom data structure that we will use for interpreting the buffer.
// We recommend keeping this under 64 bytes total.  If you change the
// data format, make sure to update the corresponding code in
// a_star.py on the Raspberry Pi.

struct Data {
    bool yellow, green, red;
    bool buttonA, buttonB, buttonC;

    int16_t leftMotor, rightMotor;
    uint16_t batteryMillivolts;
    uint16_t distances[3];
    
    bool playNotes;
    char notes[14];

    int16_t leftEncoder, rightEncoder;
    
    uint32_t turnAngle;
    int16_t turnRate;
    
    bool resetGyro;
    bool calibrateGyro;
};

PololuRPiSlave<struct Data,5> slave;
PololuBuzzer buzzer;
Romi32U4Motors motors;
Romi32U4ButtonA buttonA;
Romi32U4ButtonB buttonB;
Romi32U4ButtonC buttonC;
Romi32U4Encoders encoders;
LSM6 imu;

void setup() {
    // Set up the slave at I2C address 20.
    slave.init(20);
    
    // Initialize and calibrate gyroscope
    turnSensorSetup();

    // Play startup sound.
    buzzer.play("v10>>g16>>>c16");    
}

void loop() {
    // Read the gyro to update turnAngle, the estimation of how far
    // the robot has turned, and turnRate, the estimation of how
    // fast it is turning.
    turnSensorUpdate();
    
    // Call updateBuffer() before using the buffer, to get the latest
    // data including recent master writes.
    slave.updateBuffer();
  
    // Write various values into the data structure.
    slave.buffer.buttonA = buttonA.isPressed();
    slave.buffer.buttonB = buttonB.isPressed();
    slave.buffer.buttonC = buttonC.isPressed();
  
    // Change this to readBatteryMillivoltsLV() for the LV model.
    slave.buffer.batteryMillivolts = readBatteryMillivolts();
  
    // Read analog distnance sensor values
    slave.buffer.distances[0] = analogRead(LEFT_SENSOR_PIN);
    slave.buffer.distances[1] = analogRead(CENTER_SENSOR_PIN);
    slave.buffer.distances[2] = analogRead(LEFT_SENSOR_PIN);
    
    // Set gyro data
    slave.buffer.turnAngle = turnAngle;
    slave.buffer.turnRate = turnRate;
  
    // READING the buffer is allowed before or after finalizeWrites().
    ledYellow(slave.buffer.yellow);
    ledGreen(slave.buffer.green);
    ledRed(slave.buffer.red);
    
    motors.setSpeeds(slave.buffer.leftMotor, slave.buffer.rightMotor);
  
    // Playing music involves both reading and writing, since we only
    // want to do it once.    
    if (slave.buffer.playNotes) {
        buzzer.play(slave.buffer.notes);
        slave.buffer.playNotes = false;
    }
    
    // Note: this blocks for a while, could cause problems?
    if (slave.buffer.calibrateGyro) {
        turnSensorCalibrate();
        slave.buffer.calibrateGyro = false;
    }
    
    if (slave.buffer.resetGyro) {
        turnSensorReset();
        slave.buffer.resetGyro = false;
    }
    
    slave.buffer.leftEncoder = encoders.getCountsLeft();
    slave.buffer.rightEncoder = encoders.getCountsRight();
      
    // When you are done WRITING, call finalizeWrites() to make modified
    // data available to I2C master.
    slave.finalizeWrites();
}
