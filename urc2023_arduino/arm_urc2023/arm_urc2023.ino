// Header files
#include <ros.h>
#include <std_msgs/String.h>
#include <Wire.h> //include Wire.h library

// Define some vaiables

// Define Pins
#define base_pin_a 8 // pwm
#define base_pin_b 7 // pwm
#define base_speed 250

#define shoulder_pin_a 10 // pwm
#define shoulder_pin_b 11 // pwm
#define shoulder_speed 250

#define elbow_pin_a 3 // pwm
#define elbow_pin_b 5// pwm
#define elbow_speed 250

#define pitch_pin 4 //
#define yaw_pin 12  //

#define roll_pin_a A1 //
#define roll_pin_b A0 //

#define gripper_pin_a A3 //
#define gripper_pin_b A2 //

#define screw_pin_a 6 //
#define screw_pin_b 9 //

#define press_pin_a 2 //
#define press_pin_b 13 // //don't get mad at me, this has to be adjusted as the solenoid is running from L298

int last_state_pitch = 135;
int last_state_yaw = 135;

// I2C Adresses (Currently there can be a maximum of 6, base-shoulder-elbow-pitch-yaw-roll)
#define addr_mux 0x70

#define addr_encdr 0x36

#define ANGLE_RAW 1
#define ANGLE_DEG 2
#define ANGLE_RAD 3

#define mag_MD 0
#define mag_ML 1
#define mag_MH 2

#define pitch_servo_limit_LOW 5
#define pitch_servo_limit_HIGH 130
#define yaw_servo_limit_LOW 10
#define yaw_servo_limit_HIGH 175

#define BASE_ARRAY_INDEX 0
#define SHOULDER_ARRAY_INDEX 1
#define ELBOW_ARRAY_INDEX 2
#define PITCH_ARRAY_INDEX 3
#define YAW_ARRAY_INDEX 4
// #define ROLL_ARRAY_INDEX
// #define GRIPPER_ARRAY_INDEX
// #define PRESS_ARRAY_INDEX
// #define SCREW_ARRAY_INDEX

void TCA9548A(uint8_t bus) // Function for selecting bus-th encoder
{
  Wire.beginTransmission(0x70); // TCA9548A address is 0x70
  Wire.write(1 << bus);         // send byte to select bus
  Wire.endTransmission();
}

// necessary variables
// int addr_list[6] = {addr_encdr, addr_encdr, addr_encdr, addr_encdr, addr_encdr, addr_encdr};
#define addr_list \
  (int[]) { addr_encdr, addr_encdr, addr_encdr, addr_encdr, addr_encdr, addr_encdr }
int curr_angle[6];
int targ_angle[6];
String in_cmd;
String out_cmd = "";
char data[4];
char str_data[30];
// char log_data[30];

// necessary functions
int check_I2C(int address); // checks if sensor is connected properly over I2C
int check_Magnet();         // checks is the sensor has a properly placed magnet
// int get_Angle(int address);    // outputs the degree angle
void get_all_angles();
void print_angles();
int get_raw_angle(); // outputs the raw angle
double get_angle_in(uint8_t angle_unit);
double get_angle_for(uint8_t i, uint8_t angle_unit);
void move_base(int current, int target);
void move_shoulder(int current, int target);
void move_elbow(int current, int target);
void move_pitch(int current, int target);
void move_yaw(int current, int target);
void move_roll(int command);
void move_gripper(int command);
void move_screw(int command);
void move_press(int command);
void all_stop(void);

int iter = 0;
int command = 0;

// some necessary flags for arm safety
int arm_flag = 0; // for activagte arm movement

int base_flag = 0;     // to activate encoder tracking
int shoulder_flag = 0; // to activate encoder tracking
int elbow_flag = 0;    // to activate encoder tracking
// int pitch_flag = 0; //to activate encoder tracking (currently not used)
// int yaw_flag = 0; //to activate encoder tracking (currently not used)
// int roll_flag = 0; //to activate encoder tracking (currently not used)

// int ik_flag = 0; //to activate inverse kinematics (currently not used)

// ROS stuffs
ros::NodeHandle nh;
std_msgs::String str_msg;
// std_msgs::String log_msg;
// ROS functions
void messageCb(const std_msgs::String &rec_msg)
{
  in_cmd = rec_msg.data;
}

// ROS pubs and subs
ros::Publisher ard_pub_arm("rvr_to_base_arm", &str_msg);
ros::Subscriber<std_msgs::String> ard_sub_arm("base_to_rvr_arm", &messageCb);
// ros::Publisher ard_log_arm("rvr_arm_log", &log_msg);

void setup()
{
  Serial.begin(57600);

  nh.initNode();
  nh.advertise(ard_pub_arm);
  nh.subscribe(ard_sub_arm);


  Wire.begin();           // Wire communication begin
  Wire.setClock(400000L); // fast(does not work well in 8e5)

  // declare pins
  pinMode(base_pin_a, OUTPUT);
  pinMode(base_pin_b, OUTPUT);

  pinMode(shoulder_pin_a, OUTPUT);
  pinMode(shoulder_pin_b, OUTPUT);

  pinMode(elbow_pin_a, OUTPUT);
  pinMode(elbow_pin_b, OUTPUT);

  pinMode(pitch_pin, OUTPUT);
  pinMode(yaw_pin, OUTPUT);

  pinMode(roll_pin_a, OUTPUT);
  pinMode(roll_pin_b, OUTPUT);

  pinMode(gripper_pin_a, OUTPUT);
  pinMode(gripper_pin_b, OUTPUT);

  pinMode(screw_pin_a, OUTPUT);
  pinMode(screw_pin_b, OUTPUT);

  pinMode(press_pin_a, OUTPUT);
  pinMode(press_pin_b, OUTPUT);

  // misc pins

  // declare pins

  // set all angle targets to the current encoder angles
  // so the rover arm doesn't move as soon as its powered up
  get_all_angles();
  set_all_angles();
  print_angles();
  delay(2000);
}

void loop()
{
  // delay(10);

  // Get values of all angles from encoders
  // Serial.println("get all angles...");
  get_all_angles();
  // Serial.println("get all angles done");

  // publish all angle values to ROS
  // Serial.print("outgoing: ");
  // Serial.println(out_cmd);
  out_cmd.toCharArray(str_data, (out_cmd.length() + 1));
  str_msg.data = str_data;

  if (iter > 50)
  {
    ard_pub_arm.publish(&str_msg);
    iter = 0;
  }
  out_cmd = "";
  iter++;

  // visualize all angles at once
  // print_angles();

  /*
  if(base_flag)
    digitalWrite(13,HIGH);
  else
    digitalWrite(13,LOW);
  //*/

  // START: Do something after knowing about the angles

  arm_flag = 1;
  if (in_cmd[0] == 'A')
  {
    command = in_cmd.substring(1).toInt();
    arm_flag = command;
  }
  else if ((in_cmd[0] == 'B') && (arm_flag))
  {
    targ_angle[BASE_ARRAY_INDEX] = in_cmd.substring(1).toInt();
    move_base(curr_angle[BASE_ARRAY_INDEX], targ_angle[BASE_ARRAY_INDEX]);
  }
  else if (in_cmd[0] == 'S' && arm_flag)
  {
    targ_angle[SHOULDER_ARRAY_INDEX] = in_cmd.substring(1).toInt();
    move_shoulder(curr_angle[SHOULDER_ARRAY_INDEX], targ_angle[SHOULDER_ARRAY_INDEX]);
  }
  else if (in_cmd[0] == 'E' && arm_flag)
  {
    targ_angle[ELBOW_ARRAY_INDEX] = in_cmd.substring(1).toInt();
    move_elbow(curr_angle[ELBOW_ARRAY_INDEX], targ_angle[ELBOW_ARRAY_INDEX]);
  }
  else if (in_cmd[0] == 'P' && arm_flag)
  {
    targ_angle[PITCH_ARRAY_INDEX] = in_cmd.substring(1).toInt();
    move_pitch(curr_angle[PITCH_ARRAY_INDEX], targ_angle[PITCH_ARRAY_INDEX]);
  }
  else if (in_cmd[0] == 'Y' && arm_flag)
  {
    targ_angle[YAW_ARRAY_INDEX] = in_cmd.substring(1).toInt();
    move_yaw(curr_angle[YAW_ARRAY_INDEX], targ_angle[YAW_ARRAY_INDEX]);
  }
  else if (in_cmd[0] == 'R' && arm_flag)
  {
    command = in_cmd.substring(1).toInt();
    move_roll(command);
  }
  else if (in_cmd[0] == 'G' && arm_flag)
  {
    command = in_cmd.substring(1).toInt();
    move_gripper(command);
  }
  else if (in_cmd[0] == 'X' && arm_flag)
  {
    command = in_cmd.substring(1).toInt();
    move_press(command);
  }
  else if (in_cmd[0] == 'D' && arm_flag)
  {
    command = in_cmd.substring(1).toInt();
    move_screw(command);
  }
  else if ((in_cmd[0] == 'Z') || (!arm_flag))
  {
    all_stop();
  }
  // END: Do something after knowing about the angles

  // Keep checking for base, shoulder and elbow
  // if (arm_flag)
  // {
  //   move_base(curr_angle[BASE_ARRAY_INDEX], targ_angle[BASE_ARRAY_INDEX]);
  //   move_shoulder(curr_angle[SHOULDER_ARRAY_INDEX], targ_angle[SHOULDER_ARRAY_INDEX]);
  //   move_elbow(curr_angle[ELBOW_ARRAY_INDEX], targ_angle[ELBOW_ARRAY_INDEX]);
  // }

  nh.spinOnce();
}

// defined functions
int check_I2C(int address) // checks if sensor is connected properly over I2C
{
  Wire.beginTransmission(address);
  byte error = Wire.endTransmission();
  if (error)
    return 1;
  else
    return 0;
}
int check_Magnet() // checks is the sensor has a properly placed magnet
{
  int magnetStatus = 0; // value of the status register (MD, ML, MH)

  Wire.beginTransmission(addr_encdr);
  Wire.write(0x0B);                // figure 21 - register map: Status: MD ML MH
  Wire.endTransmission();          // end transmission
  Wire.requestFrom(addr_encdr, 1); // request from the sensor

  while (Wire.available() == 0)
    ;                         // wait until there is a byte to read, i.e. wire.available() > 0
  magnetStatus = Wire.read(); // Reading the data after the request

  if (magnetStatus & (1 << 5)) // Ideally it should be 55
  {
    // snprintf(log_data, 30, "MD:Magnet Detected");
    // log_msg.data = log_data;
    // ard_log_arm.publish(&log_msg);
    return 0;
  }
  else
  {
    if (magnetStatus & (1 << 4))
    {
      // snprintf(log_data, 30, "ML:Magnet Low");
      // log_msg.data = log_data;
      // ard_log_arm.publish(&log_msg);
    }
    else
    {
      // snprintf(log_data, 30, "MH:Magnet High");
      // log_msg.data = log_data;
      // ard_log_arm.publish(&log_msg);
    }
    return 1;
  }
}
// int get_Angle(int address) // outputs the degree angle
// {
//   int lowbyte;   // raw angle 7:0
//   word highbyte; // raw angle 7:0 and 11:8
//   int rawAngle;  // final raw angle
//   int degAngle;

//   // 7:0 - bits
//   Wire.beginTransmission(address); // connect to the sensor
//   Wire.write(0x0D);                // figure 21 - register map: Raw angle (7:0)
//   Wire.endTransmission();          // end transmission
//   Wire.requestFrom(address, 1);    // request from the sensor
//   unsigned long t = millis();
//   while (Wire.available() == 0 && (millis() - t) < 5000)
//     ;                    // wait until it becomes available and timeout 5 seconds
//   lowbyte = Wire.read(); // Reading the data after the request

//   // 11:8 - 4 bits
//   Wire.beginTransmission(address);
//   Wire.write(0x0C); // figure 21 - register map: Raw angle (11:8)
//   Wire.endTransmission();
//   Wire.requestFrom(address, 1);

//   while (Wire.available() == 0)
//     ;
//   highbyte = Wire.read();

//   highbyte = highbyte << 8;      // shifting to left
//   rawAngle = highbyte | lowbyte; // int is 16 bits (as well as the word)
//   // Serial.println(rawAngle);

//   degAngle = ((rawAngle / 4096.0) * 360.0);
//   return degAngle;
// }
void get_all_angles()
{
  // First check status of the MUX
  if (check_I2C(addr_mux) == 0)
    itoa(100, data, 10);
  else
    itoa(150, data, 10);

  out_cmd = out_cmd + data + ",";

  // Get all the angles by looping through the adress array (all 6, whether or not they are connected, the code will work)
  for (int i = 0; i < 6; i++)
  {
    // delay(10);
    // check if mux is connected
    if (check_I2C(addr_mux) == 0)
    {
      // set mux to correct channel
      TCA9548A(i);
      if (check_I2C(addr_list[i]))
      {
        // Serial.print("Sensor not connected at mux line: ");Serial.println(i);
        // snprintf(log_data, 30, "600:EncoderNotFound:%d", i);
        // log_msg.data = log_data;
        // ard_log_arm.publish(&log_msg);
        curr_angle[i] = 600;
        itoa(curr_angle[i], data, 10);
      }
      else if (check_Magnet())
      {
        // Serial.print("Magnet is  misplaced at mux line: ");Serial.println(i);
        // snprintf(log_data, 30, "500:MagnetNotFound:%d", i);
        // log_msg.data = log_data;
        // ard_log_arm.publish(&log_msg);
        curr_angle[i] = 500;
        itoa(curr_angle[i], data, 10);
      }
      else
      {
        // Serial.print("Sensor & Magnet OK at mux line: ");Serial.println(i);
        curr_angle[i] = get_angle_in(ANGLE_DEG);
        // snprintf(log_data, 30, "Sensor&mag OK:%d:%d", i, curr_angle[i]);
        // log_msg.data = log_data;
        // ard_log_arm.publish(&log_msg);
        // Serial.println(curr_angle[i]);
        itoa(curr_angle[i], data, 10);
      }
    }
    else
    {
      // snprintf(log_data, 30, "450:Mux not connected:%d", i);
      // log_msg.data = log_data;
      // ard_log_arm.publish(&log_msg);
      curr_angle[i] = 450;
      itoa(curr_angle[i], data, 10);
    }
    // append on the big string
    out_cmd = out_cmd + data + ",";
  }
}
void set_all_angles()
{
  for (int i = 0; i < 6; i++)
    targ_angle[i] = curr_angle[i];
}
void print_angles() // visualize all angles at once
{
  for (int i = 0; i < 6; i++)
  {
    Serial.print(targ_angle[i]);
    Serial.print(" ");
    Serial.print(curr_angle[i]);
    Serial.print("   ");
  }
  Serial.println();
}

void move_base(int current, int target)
{
  // Serial.print("base stby  ");

  // manual movement
  if (target == 400)
    base_flag = 1;
  if (target == 500)
  {
    analogWrite(base_pin_a, base_speed);
    analogWrite(base_pin_b, 0);
    base_flag = 0;
  }
  else if (target == 600)
  {
    analogWrite(base_pin_a, 0);
    analogWrite(base_pin_b, base_speed);
    base_flag = 0;
  }
  else if (target == 700)
  {
    analogWrite(base_pin_a, 0);
    analogWrite(base_pin_b, 0);
    base_flag = 0;
  }
  // encoder movement
  else if ((current <= 360) && (base_flag))
  {
    if (target > current)
    {
      analogWrite(base_pin_a, 0);
      analogWrite(base_pin_b, base_speed);
    }
    else if (target < current)
    {
      analogWrite(base_pin_a, base_speed);
      analogWrite(base_pin_b, 0);
    }
    else
    {
      analogWrite(base_pin_a, 0);
      analogWrite(base_pin_b, 0);
    }
  }
}
void move_shoulder(int current, int target)
{
  // Serial.print("shoulder stby  ");

  // manual movement
  if (target == 400)
    shoulder_flag = 1;
  else if (target == 500)
  {
    analogWrite(shoulder_pin_a, shoulder_speed);
    analogWrite(shoulder_pin_b, 0);
    shoulder_flag = 0;
  }
  else if (target == 600)
  {
    analogWrite(shoulder_pin_a, 0);
    analogWrite(shoulder_pin_b, shoulder_speed);
    shoulder_flag = 0;
  }
  else if (target == 700)
  {
    analogWrite(shoulder_pin_a, 0);
    analogWrite(shoulder_pin_b, 0);
    shoulder_flag = 0;
  }
  // encoder movement
  else if ((current <= 360) && (shoulder_flag))
  {
    if (target > current)
    {
      analogWrite(shoulder_pin_a, 0);
      analogWrite(shoulder_pin_b, shoulder_speed);
    }
    else if (target < current)
    {
      analogWrite(shoulder_pin_a, base_speed);
      analogWrite(shoulder_pin_b, 0);
    }
    else
    {
      analogWrite(shoulder_pin_a, 0);
      analogWrite(shoulder_pin_b, 0);
    }
  }
}
void move_elbow(int current, int target)
{
  // Serial.print("elbow stby  ");

  // manual movement
  if (target == 400)
    elbow_flag = 1;
  else if (target == 500)
  {
    analogWrite(elbow_pin_a, 0);
    analogWrite(elbow_pin_b, base_speed);
    elbow_flag = 0;
  }
  else if (target == 600)
  {
    analogWrite(elbow_pin_a, base_speed);
    analogWrite(elbow_pin_b, 0);
    elbow_flag = 0;
  }
  else if (target == 700)
  {
    analogWrite(elbow_pin_a, 0);
    analogWrite(elbow_pin_b, 0);
    elbow_flag = 0;
  }
  // encoder movement
  else if ((current <= 360) && (elbow_flag))
  {
    if (target > current)
    {
      analogWrite(elbow_pin_a, 0);
      analogWrite(elbow_pin_b, base_speed);
    }
    else if (target < current)
    {
      analogWrite(elbow_pin_a, base_speed);
      analogWrite(elbow_pin_b, 0);
    }
    else
    {
      analogWrite(elbow_pin_a, 0);
      analogWrite(elbow_pin_b, 0);
    }
  }
}
void move_pitch(int current, int target)
{
  // Serial.print("pitch stby  ");
  if ((last_state_pitch != target))
  {
    if (target > last_state_pitch)
    {
      while (target != last_state_pitch)
      {
        int onTime = map(last_state_pitch, 0, 270, 500, 2500);
        int offTime = 20000 - onTime;
        digitalWrite(pitch_pin, HIGH);
        delayMicroseconds(onTime);
        digitalWrite(pitch_pin, LOW);
        delayMicroseconds(offTime);
        delay(30);
        last_state_pitch = last_state_pitch + 1;
      }
    }
    else if (target < last_state_pitch)
    {
      while (target != last_state_pitch)
      {
        int onTime = map(last_state_pitch, 0, 270, 500, 2500);
        int offTime = 20000 - onTime;
        digitalWrite(pitch_pin, HIGH);
        delayMicroseconds(onTime);
        digitalWrite(pitch_pin, LOW);
        delayMicroseconds(offTime);
        delay(30);
        last_state_pitch = last_state_pitch - 1;
      }
    }
  }
  // delay(250);
}
void move_yaw(int current, int target)
{
  // Serial.print("yaw stby  ");
  if (last_state_yaw != target)
  {
    if (target > last_state_yaw)
    {
      while (target != last_state_yaw)
      {
        int onTime = map(last_state_yaw, 0, 270, 500, 2500);
        int offTime = 20000 - onTime;
        digitalWrite(yaw_pin, HIGH);
        delayMicroseconds(onTime);
        digitalWrite(yaw_pin, LOW);
        delayMicroseconds(offTime);
        delay(30);
        last_state_yaw = last_state_yaw + 1;
      }
    }
    else if (target < last_state_yaw)
    {
      while (target != last_state_yaw)
      {
        int onTime = map(last_state_yaw, 0, 270, 500, 2500);
        int offTime = 20000 - onTime;
        digitalWrite(yaw_pin, HIGH);
        delayMicroseconds(onTime);
        digitalWrite(yaw_pin, LOW);
        delayMicroseconds(offTime);
        delay(30);
        last_state_yaw = last_state_yaw - 1;
      }
    }
  }
  // delay(250);
}
void move_roll(int command)
{
  // Serial.print("roll stby  ");

  if (command == 1)
  {
    digitalWrite(roll_pin_a, HIGH);
    digitalWrite(roll_pin_b, LOW);
    delay(50);
  }
  else if (command == 2)
  {
    digitalWrite(roll_pin_a, LOW);
    digitalWrite(roll_pin_b, HIGH);
    delay(50);
  }
  else
  {
    digitalWrite(roll_pin_a, LOW);
    digitalWrite(roll_pin_b, LOW);
  }
}
void move_gripper(int command)
{
  // Serial.print("gripper stby  ");

  if (command == 1)
  {
    digitalWrite(gripper_pin_a, HIGH);
    digitalWrite(gripper_pin_b, LOW);
    delay(50);
  }
  else if (command == 2)
  {
    digitalWrite(gripper_pin_a, LOW);
    digitalWrite(gripper_pin_b, HIGH);
    delay(50);
  }
  else
  {
    digitalWrite(gripper_pin_a, LOW);
    digitalWrite(gripper_pin_b, LOW);
  }
}
void move_screw(int command)
{
  // Serial.print("screw stby  ");

  if (command == 1)
  {
    digitalWrite(screw_pin_a, HIGH);
    digitalWrite(screw_pin_b, LOW);
    delay(50);
  }
  else if (command == 2)
  {
    digitalWrite(screw_pin_a, LOW);
    digitalWrite(screw_pin_b, HIGH);
    delay(50);
  }
  else
  {
    digitalWrite(screw_pin_a, LOW);
    digitalWrite(screw_pin_b, LOW);
  }
}
void move_press(int command)
{
  if (command == 1)
  {
    digitalWrite(press_pin_a, HIGH);
    digitalWrite(press_pin_b, LOW);
  }
  else if (command == 2)
  {
    digitalWrite(press_pin_a, LOW);
    digitalWrite(press_pin_b, HIGH);
  }
  else
  {
    digitalWrite(press_pin_a, LOW);
    digitalWrite(press_pin_b, LOW);
  }
}
void all_stop(void)
{
  // stop everything and deactivate all flags

  base_flag = 0;
  shoulder_flag = 0;
  elbow_flag = 0;

  analogWrite(base_pin_a, 0);
  analogWrite(base_pin_b, 0);

  digitalWrite(shoulder_pin_a, LOW);
  digitalWrite(shoulder_pin_b, LOW);

  analogWrite(elbow_pin_a, 0);
  analogWrite(elbow_pin_b, 0);

  digitalWrite(pitch_pin, LOW);
  digitalWrite(yaw_pin, LOW);

  digitalWrite(roll_pin_a, LOW);
  digitalWrite(roll_pin_b, LOW);

  digitalWrite(gripper_pin_a, LOW);
  digitalWrite(gripper_pin_b, LOW);

  digitalWrite(press_pin_a, LOW);
  digitalWrite(press_pin_b, LOW);
}

int get_raw_angle() // outputs the raw angle
{
  int16_t rawAngle;
  // 7:0 - bits
  Wire.beginTransmission(addr_encdr); // connect to the sensor
  Wire.write(0x0D);                   // figure 21 - register map: Raw angle (7:0)
  Wire.endTransmission();             // end transmission
  Wire.requestFrom(addr_encdr, 1);    // request from the sensor
  unsigned long t = millis();
  while (Wire.available() == 0 && (millis() - t) < 5000)
    ;                     // wait until it becomes available and timeout 5 seconds
  rawAngle = Wire.read(); // Reading the data after the request

  // 11:8 - 4 bits
  Wire.beginTransmission(addr_encdr);
  Wire.write(0x0C); // figure 21 - register map: Raw angle (11:8)
  Wire.endTransmission();
  Wire.requestFrom(addr_encdr, 1);
  t = millis();
  while (Wire.available() == 0 && (millis() - t) < 5000)
    ;
  rawAngle = rawAngle | (Wire.read() << 8); // shifting high bytes to the left
  // Serial.println(rawAngle);

  return rawAngle;
}

double get_angle_in(uint8_t angle_unit)
{
  if (angle_unit == ANGLE_DEG)
  {
    return get_raw_angle() * (360.0 / 4096.0); // total 4096 steps in one rev
  }
  else if (angle_unit == ANGLE_RAD)
  {
    return get_raw_angle() * (TWO_PI / 4096.0); // total 4096 steps in one rev
  }
  else
  {
    return get_raw_angle();
  }
}

// i : which bus(at the mux)
// angle_unit : either of these macros: ANGLE_RAW, ANGLE_DEG, or ANGLE_RAD
double get_angle_for(uint8_t i, uint8_t angle_unit)
{
  TCA9548A(i);
  return get_angle_in(angle_unit);
}
