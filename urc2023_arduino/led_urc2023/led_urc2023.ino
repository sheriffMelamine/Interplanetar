#include <ros.h>
#include <std_msgs/String.h>

#define RED 9
#define GREEN 11
#define BLUE 10


int i=0;
String in_cmd;
ros::NodeHandle nh;

void ledCallback( const std_msgs::String& led){
  in_cmd = led.data;
}

ros::Subscriber<std_msgs::String> sub("/LED",ledCallback);

void setup() {
  pinMode(RED,OUTPUT);
  pinMode(GREEN,OUTPUT);
  pinMode(BLUE,OUTPUT);

  digitalWrite(RED,HIGH);
  digitalWrite(GREEN,HIGH);
  digitalWrite(BLUE,HIGH);

  nh.initNode();
  nh.subscribe(sub);
  
  delay(2000); 
}

void loop() {
  if(i>30000)i=0;
  if(in_cmd==String("red")){
      digitalWrite(RED,LOW);
      digitalWrite(GREEN,HIGH);
     digitalWrite(BLUE,HIGH);
  }
  else if(in_cmd==String("green")){
      if(i<15000)
      digitalWrite(GREEN,LOW);
      else
      digitalWrite(GREEN,HIGH);
      
      digitalWrite(RED,HIGH);
      digitalWrite(BLUE,HIGH);
  }
  else if(in_cmd==String("blue")){
    digitalWrite(BLUE,LOW);
    digitalWrite(RED,HIGH);
    digitalWrite(GREEN,HIGH);
  }
  else{
  digitalWrite(RED,HIGH);
  digitalWrite(GREEN,HIGH);
  digitalWrite(BLUE,HIGH);
  }
  i++;
  nh.spinOnce();
}
