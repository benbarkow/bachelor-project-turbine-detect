#include <Arduino.h>

class BeschlStepper{
  private:
  int stepsPerRevolution;
  int stepsLeft, stepsForMove;
  double maxV = 0.0; //maximum velocity in Umdrehungen/s
  float dis = 0.0; //distanz zurueckzulegen in Umdrehungen
  int timeInterval = 0; //Zeitintervall zwischen jedem halben step also von HIGH->LOW oder LOW->HIGH
  float acceleration = 20.0; //Umdrehungen/s^2
  float servoAngle = 0.0;
  float gearratio = 1.0; //when the motor is attached to a gear the gearratio can be set. The acceleration and velocity still apply to the motor
  unsigned long prevMicros = 0, moveTime = 0;
  byte stepPin, dirPin;
  boolean moveRunning = false,stepTracker = false, plannedMove = true;

  public:

 /**
 * initilizes a Steppermotor
 * @param s the Steppin
 * @param d the directionpin
 * @param stepsRev the number of steps per Revolution
*/
 void initialize(int s,int d, int stepsRev){
    stepPin = s;
    dirPin = d;
    stepsPerRevolution = stepsRev;
    pinMode(stepPin,OUTPUT);
    pinMode(dirPin,OUTPUT);
    pinMode(LED_BUILTIN,OUTPUT);
  }

/**
 * sets the order to drive the motor a certain distance
 * @param distance the distance to drive the motor in Revolutions
 * @param vel the maximum velocity to drive the motor at in Revolutions/s
 * @param dir the direction the motor is turning
 * @return the time it takes the move to complete in seconds
*/
  float runMotor(float distance, float vel, boolean dir){
    if(!moveRunning){
      digitalWrite(dirPin,dir);
      dis = distance*gearratio;
      stepsForMove = distance*stepsPerRevolution;
      stepsLeft = stepsForMove;
      maxV = vel;
      timeInterval = 0;
      // Serial.print("sl in rm: "); Serial.println(stepsLeft);

      moveRunning = true;
      plannedMove = true;
      //calculation of the time required for the move
      float s = maxV*maxV/(2.0*acceleration);
      moveTime = micros();
      float calcMoveTime = (maxV-sqrt(maxV*maxV-2.0*acceleration*dis))/acceleration;
      // if(s < dis/2.0) calcMoveTime = 2.0*maxV/acceleration + (dis-2.0*s)/maxV;
      // else calcMoveTime = 2.0*sqrt(dis/acceleration);
      // Serial.print("calculated time: "); Serial.print(calcMoveTime); Serial.println("s");
      return calcMoveTime; 
    }
    return -1;
  }

  

  /**
   * sets the order to drive the motor a certain distance
   * @param distance the distance to drive the motor in Revolutions
   * @param time the time in which the motor must reach its target in seconds
   * @param dir the direction the motor is turning
  */
    void runMotorTimed(float distance, float time, boolean dir){
      if(!moveRunning){
        digitalWrite(dirPin,dir);
        dis = distance*gearratio;
        stepsForMove = distance*stepsPerRevolution;
        stepsLeft = stepsForMove;
        float athalf = acceleration*time/2.0;
        float root = sqrt(athalf*athalf-acceleration*dis);
        maxV = athalf + root;
        timeInterval = 0;
        Serial.println(maxV);
        if(maxV*maxV/(2.0*acceleration) > dis/2.0) maxV = athalf - root;
        moveRunning = true;
        plannedMove = true;
        Serial.println(maxV);
        moveTime = micros();
      }
    }

  

  /**
   * sets the angle to drive to
   * @param angle the angle to drive to
   * @param vel the maximum velocity for the move in Revolutions/s
   * @return the it takes to make the move in seconds
  */
  float setServoAngle(float angle, float vel){
    if(!moveRunning){
      float deltaAngle = angle - servoAngle;
      digitalWrite(dirPin,deltaAngle > 0);
      servoAngle = angle;
      maxV = vel; 
      dis = abs(deltaAngle)*gearratio/360.0;
      stepsForMove = dis*stepsPerRevolution;
      stepsLeft = stepsForMove;
      timeInterval = 0;
      moveRunning = true;
      plannedMove = true;
      float s = maxV*maxV/(2.0*acceleration);
      if(s < dis/2.0) return 2.0*maxV/acceleration + (dis-2.0*s)/maxV;
      else return 2.0*sqrt(dis/acceleration);
    }
    return -1;
  }


  /**
   * sets the angle to drive to with given time and calculates the maxium velocity
   * @param angle the angle to drive to
   * @param time the time is must take the move to complete in seconds
  */
  void setServoAngleTimed(float angle, float time){
    if(!moveRunning){
      float deltaAngle = angle - servoAngle;
      digitalWrite(dirPin,deltaAngle > 0);
      servoAngle = angle;
      dis = abs(deltaAngle)*gearratio/360.0;
      stepsForMove = dis*stepsPerRevolution;
      stepsLeft = stepsForMove;
      timeInterval = 0;
      float athalf = acceleration*time/2.0;
      float root = sqrt(athalf*athalf-acceleration*dis);
      maxV = athalf + root;
      if(maxV*maxV/(2.0*acceleration) > dis/2.0) maxV = athalf - root;
      moveRunning = true;
      plannedMove = true;
    }
  }

  void runMotorUntilStop(float vel, bool dir){
    digitalWrite(dirPin,dir);
    timeInterval = 1000000.0/float(stepsPerRevolution*2*vel);
    moveRunning = true;
    plannedMove = false;
    stepsLeft = 1;
  }

  void stopMotor(){
    stepsLeft = 0;
    moveRunning = false;
  }

  /**
   * updates the Motor while not stopping the code by holding it in a loop
  */
  void updateMotor(){
    digitalWrite(LED_BUILTIN,moveRunning);
    if(moveRunning){
      //geschwindigkeitsgraph tri(x)=a*t0/2 *(1-abs((x-t0/2)/(t0/2)))
      //mit der beschleunigung a und distanz t0
      if(stepsLeft == 0){
        moveRunning = false;
        // Serial.print("move done in "); Serial.print((micros()-moveTime)/1000000.0); Serial.println("s");
        return;
      }
      // Serial.print(timeInterval); Serial.print(" , "); Serial.println(prevMicros);
      if(micros() - prevMicros > timeInterval){
        // Serial.println("pulse");
        digitalWrite(stepPin,stepTracker);
        stepTracker = !stepTracker;
        prevMicros = micros();
        if(stepTracker){
          if(plannedMove){
            stepsLeft--;
            float x = float(stepsForMove-stepsLeft)/float(stepsPerRevolution);
            float dishalf = dis/2;
            float currentVel = min(acceleration*dishalf*(1-abs((x-dishalf)/dishalf))+0.25, maxV);
            timeInterval = 1000000.0/float(stepsPerRevolution*2.0*currentVel);
            // Serial.print("stepsLeft: "); Serial.println(stepsLeft);
          }
        }
      }
    }
  }

  /**
   * setter for the acceleration
   * @param a the new acceleration in Revolution/s^2
  */
  void setAcceleration(float a){
    acceleration = a;
  }

  /**
   * sets the current Position of the Servo to zero
  */
  void setServoZero(){
    servoAngle = 0;
  }

  /**
   * setter for the gearratio
   * @param g the new gearratio. The motor makes g revolutions for the output of the gearbox to make one revolution
  */
  void setGearRatio(float g){
    gearratio = g;
  }

  boolean isDone(){
    return !moveRunning;
  }

};