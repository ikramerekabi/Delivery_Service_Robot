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
std_msgs::String str_msgchatter; 
char paid[1] = "0";
char hello[13] = "Hello";
ros::Publisher payment("payment", &str_msg);
ros::Publisher chatter("chatter", &str_msgchatter); 

void setup() 
{ 
 nh.initNode();
 nh.loginfo("RagTag RFID Payments");

  //MY RFID SETUP
  Serial.begin(57600);   // Initiate a serial communication
  SPI.begin();      // Initiate  SPI bus
  mfrc522.PCD_Init();   // Initiate MFRC522
  Serial.println("Approximate your card to the reader...");
  Serial.println();
  nh.advertise(payment);
  nh.advertise(chatter);


}
void loop() 
{

  //RFID
  // Look for new cards
  if ( ! mfrc522.PICC_IsNewCardPresent()) 
  {
    return;
  }
  // Select one of the cards
  if ( ! mfrc522.PICC_ReadCardSerial()) 
  {
    return;
  }
  //Show UID on serial monitor
  Serial.print("UID tag :");
  String content= "";
  byte letter;
  for (byte i = 0; i < mfrc522.uid.size; i++) 
  {
     //Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
     //Serial.print(mfrc522.uid.uidByte[i], HEX);
     content.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " "));
     content.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
  Serial.println();
  Serial.print("Message : ");
  content.toUpperCase();
  if (content.substring(1) == "03 BE C3 E9" || content.substring(1) == "45 A6 3B D9") //change here the UID of the card/cards that you want to give access
  {
    paid[1]  = "1";
    str_msg.data = paid;
    payment.publish( &str_msg );

    str_msgchatter.data = hello;
    chatter.publish( &str_msgchatter );    
 
    Serial.println("Authorized access");
    Serial.println();
    delay(3000);
  }
 
 else   {
    Serial.println(" Access denied");
    delay(3000);
  }
} 
