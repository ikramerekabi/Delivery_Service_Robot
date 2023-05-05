//This code is to use with FC51 IR proximity sensor, when it detects an obstacle it lights the internal LED
//of the Arduino Board, refer to www.Surtrtech.com for more information

#include <ros.h>
#include <std_msgs/Empty.h>
#include <std_msgs/String.h>
#include <string.h>

const int ProxSensor=3; //Declaring where the Out pin from the sensor is wired
ros::NodeHandle  nh;
std_msgs::String str_msg; 

ros::Publisher ledsensor("ledsensor", &str_msg);

void setup() {                
  pinMode(13, OUTPUT);   // setting the pin modes, the "13" stands for the internal Arduino uno internal LED  
  pinMode(ProxSensor,INPUT); // then we have the out pin from the module
  //Serial.begin(9600);   // Initiate a serial communication
  nh.initNode();
  nh.loginfo("RagTag LED Loader and Unloader Sensor");
  nh.advertise(ledsensor);

}

void loop() {
  
  if(digitalRead(ProxSensor)==HIGH)      //Check the sensor output if it's high
   {
     Serial.println("Authorized access by LOW");
     digitalWrite(13, LOW);   // Turn the LED on (Yes by writing LOW)
   }
  else
   {
    Serial.println("Authorized access by High");
    
    str_msg.data = "1";
    ledsensor.publish( &str_msg );

    digitalWrite(13, HIGH);    // Turn the LED OFF if there's no signal on the ProxSensor
   }
  delay(2000);             

}
