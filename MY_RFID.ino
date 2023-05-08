/*
 * 
 * All the resources for this project: https://randomnerdtutorials.com/
 * Modified by Rui Santos
 * 
 * Created by FILIPEFLOP
 * 
 */
 
#include <SPI.h>
#include <MFRC522.h>
 
#define SS_PIN 10
#define RST_PIN 9

#include <ros.h>
#include <std_msgs/Empty.h>
#include <std_msgs/String.h>
#include <string.h>

//FOR RFID
MFRC522 mfrc522(SS_PIN, RST_PIN);   // Create MFRC522 instance. 

ros::NodeHandle  nh;
std_msgs::String str_msg;  
char paid[1] = "0"; 
ros::Publisher payment("payment", &str_msg); 

void setup() 
{ 
 Serial.begin(57600);   // Initiate a serial communication  
  
 nh.initNode();
 nh.loginfo("RagTag RFID Payments");  
 
  //MY RFID SETUP
  SPI.begin();      // Initiate  SPI bus
  mfrc522.PCD_Init();   // Initiate MFRC522 
  nh.advertise(payment); 
}
void loop() 
{
  //Card Detected
  if (mfrc522.PICC_IsNewCardPresent()) {  
    String content= "";
    byte letter;
    
    // Read from card
    nh.loginfo("Reading from card...");    
    bool readInfo = mfrc522.PICC_ReadCardSerial();     
    for (byte i = 0; i < mfrc522.uid.size; i++) 
    {        
       content.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " "));
       content.concat(String(mfrc522.uid.uidByte[i], HEX));
    }
    content.toUpperCase(); 
    
    //If ID was read from card then subscribe to service
    if (readInfo) {
      if (content.substring(1) == "03 BE C3 E9" || content.substring(1) == "45 A6 3B D9") 
      {
       // paid[1]  = "1";
        str_msg.data = "1";
        payment.publish( &str_msg );
  
        nh.loginfo("Authorized access");  
      }
      else 
      {
       // paid[1]  = "0";
        str_msg.data = "0";
        payment.publish( &str_msg );    
 
        nh.loginfo("Access denied for ");  
      }
    }
  }
  
  delay(1500);
  nh.spinOnce();  
} 
