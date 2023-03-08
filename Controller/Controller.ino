#include "Stepper.h"

BeschlStepper XMotor;

void setup(){
  Serial.begin(9600);
  XMotor.initialize(2,5,800);
  XMotor.runMotorUntilStop(1,false);
}

void loop(){
  Serial.println(digitalRead(9));
//  String order = "";
//  if(Serial.available() > 0){
//    order = Serial.readString();
//    Serial.println(order);
//  }
  
  XMotor.updateMotor();
}
