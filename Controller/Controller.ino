#include "Stepper.h"

BeschlStepper XMotor, YMotor;

byte xEndstop = 9, yEndstop = 10;

int xPos = 0, yPos = 0;
int xMax = 470, yMax = 390; //in millimeters
boolean firstDone = false;

void setup(){
  Serial.begin(9600);
  pinMode(xEndstop,INPUT_PULLUP);
  pinMode(yEndstop,INPUT_PULLUP);
  XMotor.initialize(2,5,20);
  YMotor.initialize(3,6,20);
}

void loop(){
  // Serial.println(digitalRead(yEndstop));
  String order = "";
  if(Serial.available() > 0){
    order = Serial.readString();
  }
  if(order.equals("home")){
    homeAxis();
  }
  else if(order.equals("position")){
    Serial.print("xPos"); Serial.print(","); Serial.println("yPos");
  }
  else{
    int xOld = xPos;
    int yOld = yPos;
    if(order.substring(0,3).equals("abs")){
      // Serial.println("abs");
      
      xPos = order.substring(3,order.indexOf(',')).toInt();
      yPos = order.substring(order.indexOf(',')+1,order.length()).toInt();
    }
    else if(order.substring(0,3).equals("rel")){
      // Serial.println("rel");
      xPos += order.substring(3,order.indexOf(',')).toInt();
      yPos += order.substring(order.indexOf(',')+1,order.length()).toInt();
    }
    if(xPos < 0){
      xPos = 0;
      Serial.println("xMin reached");
    }
    if(yPos < 0){
      yPos = 0;
      Serial.println("yMin reached");
    }
    if(xPos > xMax){
      xPos = xMax;
      Serial.println("xMax reached");
    }
    if(yPos > yMax){
      yPos = yMax;
      Serial.println("yMax reached");
    }
    int deltaX = xPos - xOld;
    int deltaY = yPos - yOld;

    // if(deltaX != 0 && deltaY != 0){
    //   XMotor.runMotorTimed(abs(deltaX),4,deltaX < 0);
    //   YMotor.runMotorTimed(abs(deltaY),4,deltaY < 0);
    //   // if(abs(deltaX) > abs(deltaY)){
    //   //   // float timeNeeded = XMotor.runMotor(abs(deltaX),100,deltaX < 0);
    //   // }
    //   // else{
    //   //   float timeNeeded = YMotor.runMotor(abs(deltaY),100,deltaY < 0);
    //   //   XMotor.runMotorTimed(abs(deltaX),timeNeeded,deltaX < 0);
    //   // }
    // }
    // else if(deltaX != 0) XMotor.runMotor(abs(deltaY),100,deltaX < 0);
    // else if(deltaY != 0) YMotor.runMotor(abs(deltaY),100,deltaY < 0);
    if(deltaX != 0) XMotor.runMotor(abs(deltaX),200,deltaX < 0);
    if(deltaY != 0) YMotor.runMotor(abs(deltaY),200,deltaY < 0);
    // Serial.print("isDone: "); Serial.print(XMotor.isDone()); Serial.print(" deltaX: "); Serial.println(deltaX);
  }

  if(XMotor.isDone() && YMotor.isDone() && firstDone){
    firstDone = false;
    Serial.println("done");
  }
  else if(!XMotor.isDone() || !YMotor.isDone()){
    firstDone = true;

  }
  XMotor.updateMotor();
  YMotor.updateMotor();
}

void homeAxis(){
  bool xhoming = true;
  byte sequence = 0;
  while(xhoming){
    if(sequence == 0){
      XMotor.runMotorUntilStop(70,true);
      if(digitalRead(xEndstop)){
        XMotor.stopMotor();
        sequence = 1;
      }
    }
    else if(sequence == 1){
      XMotor.runMotor(20,60,false);
      sequence = 2;
    }
    else if(sequence == 2){
      if(XMotor.isDone()){
        sequence = 3;
      }
    }
    else if(sequence == 3){
      XMotor.runMotorUntilStop(30,true);
      if(digitalRead(xEndstop)){
        XMotor.stopMotor();
        sequence = 4;
        xhoming = false;
      }
    }
    XMotor.updateMotor();
  }
  bool yhoming = true;
  sequence = 0;
  while(yhoming){
    if(sequence == 0){
      YMotor.runMotorUntilStop(70,true);
      if(digitalRead(yEndstop)){
        YMotor.stopMotor();
        sequence = 1;
      }
    }
    else if(sequence == 1){
      YMotor.runMotor(20,60,false);
      sequence = 2;
    }
    else if(sequence == 2){
      if(YMotor.isDone()){
        sequence = 3;
      }
    }
    else if(sequence == 3){
      YMotor.runMotorUntilStop(30,true);
      if(digitalRead(yEndstop)){
        YMotor.stopMotor();
        sequence = 4;
        yhoming = false;
      }
    }
    YMotor.updateMotor();
  }
  xPos = 0;
  yPos = 0;
  Serial.println("homing done");
}