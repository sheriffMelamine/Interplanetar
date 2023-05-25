

#include <ros.h>
#include <std_msgs/String.h>

// Motor A connections
#define enA 5
#define in1 3
#define in2 A2
// Motor B connections
#define enB 9
#define in3 8
#define in4 13


/// pin for relay
#define relay1 1
#define relay2 A5
#define relay3 4
#define relay4 A4
#define relay5 A0
#define relay6 2


int relays[6] = {relay1,relay2,relay3,relay4,relay5,relay6};
int motor[6] = {enA,in1,in2,enB,in3,in4};
int mot,cmd,flag;
ros::NodeHandle  nh;
String in_cmd;
String debug;
char charArray[20];

void messageCb( const std_msgs::String& rec_msg)
{
  in_cmd = rec_msg.data;
}
ros::Subscriber<std_msgs::String> ard_sub_sci("base_to_rvr_sci", &messageCb );



void setup() {

  Serial.begin(57600);
  
  for(int i=0;i<6;i++) {
    pinMode(relays[i],OUTPUT);
    pinMode(motor[i],OUTPUT);
  }
  
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);
  
  nh.initNode();
  nh.subscribe(ard_sub_sci);

  delay(2000);

}

void loop() {
  delay(50);
  cmd = in_cmd.substring(1).toInt();
  if(in_cmd[0]=='P')
    digitalWrite(relays[cmd],HIGH);
   
  else if(in_cmd[0]=='Q')
    digitalWrite(relays[cmd],LOW);
  
  else if(in_cmd[0]=='X'){
    
    mot = 3*(cmd/3);
    flag = cmd%3;
    analogWrite(motor[mot], 245-55*mot);
    digitalWrite(motor[mot+1],flag/2);
    digitalWrite(motor[mot+2],flag%2);
    
  }  
  else
   { 
      analogWrite(enA, 0);
      analogWrite(enB, 0);
      digitalWrite(in1, LOW);
      digitalWrite(in2, LOW);
      digitalWrite(in3, LOW);
      digitalWrite(in4, LOW);
      for(int i=0;i<6;i++)
        digitalWrite(relays[i],LOW); 
   } 
   
    
   nh.spinOnce(); 
}
