#include <Arduino.h>
#include <Adafruit_PWMServoDriver.h>
#include <Wire.h>

// put function declarations here:
#define SDA 21
#define SCL 22

#define ServMin 150
#define ServMax 500



Adafruit_PWMServoDriver pca9685 = Adafruit_PWMServoDriver(0x40);

void setServo(uint8_t channel, int angle) {
  angle = constrain(angle,0,180);
  int pulse = map(angle, 0, 180, ServMin, ServMax);
  pca9685.setPWM(channel, 0, pulse);
}


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Wire.begin();

  pca9685.begin();
  pca9685.setPWMFreq(50);
  
}

void loop() {
  if(Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    int space = cmd.indexOf(' ');

  float theta0 = cmd.substring(0, space).toFloat();
  float theta1 = cmd.substring(space + 1).toFloat();

  Serial.println(theta0);
  Serial.println(theta1);

  


  

  setServo(0, theta0);
  setServo(1, theta1);

  }
}

// put function definitions here:
