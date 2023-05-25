#include <ros.h>
#include <geometry_msgs/Twist.h>

#define leftRPWMpin 9
#define leftLPWMpin 6
#define rightRPWMpin 5
#define rightLPWMpin 3

#define leftENR 2
#define leftENL 10
#define rightENR 7
#define rightENL 12

ros::NodeHandle nh;
//String debug;
//char charArray[40];

int vel1 = 0;
int vel2 = 0;

float x=0; 
float z=0; 

void velCallback( const geometry_msgs::Twist& vel) {
  
  x = vel.linear.x;
  z = vel.angular.z;
  if(x!=0.&&z!=0.){
    x*=0.531269;
    z*=0.531269;
  }
  
  vel1 = round(255.*constrain(x+z,-1.,1.));
  vel2 = round(255.*constrain(x-0.5*z,-1.,1.));
  
}

ros::Subscriber<geometry_msgs::Twist> sub("/cmd_vel", velCallback);

void traverse(){
  if(vel1<0){
    analogWrite(leftLPWMpin,0);
    analogWrite(leftRPWMpin,-vel1);
  }
  else{
    analogWrite(leftLPWMpin,vel1);
    analogWrite(leftRPWMpin,0);
  }
  if(vel2<0){
    analogWrite(rightLPWMpin,0);
    analogWrite(rightRPWMpin,-vel2);
  }
  else{
    analogWrite(rightLPWMpin,vel2);
    analogWrite(rightRPWMpin,0);
  }
  //debug = "Wheel1: "+String(vel1)+", Wheel2: "+String(vel2);
  
 
}


void setup() {
 
  
  Serial.begin(57600);
  pinMode(leftENR, OUTPUT);
  pinMode(leftENL, OUTPUT);
  pinMode(rightENR, OUTPUT);
  pinMode(rightENL, OUTPUT);

  pinMode(leftRPWMpin, OUTPUT);
  pinMode(leftLPWMpin, OUTPUT);
  pinMode(rightRPWMpin, OUTPUT);
  pinMode(rightLPWMpin, OUTPUT);

  digitalWrite(leftENR, HIGH);
  digitalWrite(leftENL, HIGH);
  digitalWrite(rightENR, HIGH);
  digitalWrite(rightENL, HIGH);
  nh.initNode();
  nh.subscribe(sub);
  delay(2000);
}

void loop() {
    
   
    traverse();
    
    
    //debug.toCharArray(charArray,debug.length()+1);
    //nh.loginfo(charArray);
    nh.spinOnce();
    

}
