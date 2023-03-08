#include "Stepper.h"

BeschlStepper XMotor, YMotor;

byte xEndstop = 9, yEndstop = 10;

void setup(){
  Serial.begin(9600);
  pinMode(xEndstop,INPUT_PULLUP);
  pinMode(yEndstop,INPUT_PULLUP);
  XMotor.initialize(2,5,800);
  YMotor.initialize(3,6,800);
}

void loop(){
  // Serial.println(digitalRead(yEndstop));
  String order = "";
  if(Serial.available() > 0){
    order = Serial.readString();
    Serial.println(order);
  }
  if(order.equals("home")){
    homeAxis();
  }
  
  XMotor.updateMotor();
}

void homeAxis(){
  bool xhoming = true;
  byte sequence = 0;
  while(xhoming){
    if(sequence == 0){
      XMotor.runMotorUntilStop(2,true);
      if(digitalRead(xEndstop)){
        Serial.println("x seq 0");
        XMotor.stopMotor();
        sequence = 1;
      }
    }
    else if(sequence == 1){
      Serial.println("x seq 1");
      XMotor.runMotor(0.5,2,false);
      sequence = 2;
    }
    else if(sequence == 2){
      if(XMotor.isDone()){
        Serial.println("x seq 2");
        sequence = 3;
      }
    }
    else if(sequence == 3){
      XMotor.runMotorUntilStop(0.5,true);
      if(digitalRead(xEndstop)){
        Serial.println("x seq 3");
        XMotor.stopMotor();
        sequence = 4;
        xhoming = false;
      }
    }
    // Serial.println(sequence);
    XMotor.updateMotor();
  }

  Serial.println("x done");
  bool yhoming = true;
  sequence = 0;
  while(yhoming){
    if(sequence == 0){
      YMotor.runMotorUntilStop(2,true);
      if(digitalRead(yEndstop)){
        Serial.println("y seq 0");
        YMotor.stopMotor();
        sequence = 1;
      }
    }
    else if(sequence == 1){
      Serial.println("y seq 1");
      YMotor.runMotor(3,2,false);
      sequence = 2;
    }
    else if(sequence == 2){
      Serial.println(YMotor.isDone());
      if(YMotor.isDone()){
        Serial.println("y seq 2");
        sequence = 3;
      }
    }
    else if(sequence == 3){
      YMotor.runMotorUntilStop(0.5,true);
      if(digitalRead(yEndstop)){
        Serial.println("y seq 3");
        YMotor.stopMotor();
        sequence = 4;
        yhoming = false;
      }
    }
    YMotor.updateMotor();
  }
  Serial.println("homing done");
}