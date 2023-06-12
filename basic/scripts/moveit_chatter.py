#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from sensor_msgs.msg import JointState as JS
from sensor_msgs.msg import Joy
from math import pi

def map_range(x,a,b,c,d):
    return (x-a)*(d-c)/(b-a) + c 

anglemin = [5.,140.,206.,5.,0.,10.]
anglemax = [245.,200.,256.,130.,0.,175.]


urdfmin = [-2.*pi/3.,-1.,-0.5,1.2217,0.,.8727]
urdfmax = [2.*pi/3.,0.,0.7837,-1.2217,0.,-.8727]

flag = False
msg = ["B125","S200","E225","P68","","Y92"]
joint=["B","S","E","P","R","Y"]

button = rospy.get_param("myjoy/button/LB")
plan_flag = False
oldbtn = 0

def callback(data):
    global flag,msg
    flag=True
   
    for i in range(6):
        #rospy.loginfo(rospy.get_caller_id() + "I heard %s is  %f",data.name[i],data.position[i])
        if i==4:
            continue
        msg[i] = joint[i]+str((int(round(map_range(data.position[i],urdfmin[i],urdfmax[i],anglemin[i],anglemax[i]))))%360)

def callbackjoy(data):
    global oldbtn, button, plan_flag
    if data.buttons[button]==0 and oldbtn==1:
        plan_flag = True
    oldbtn = data.buttons[button]
    
    
def talker():
    rospy.init_node('moveit_workaround', anonymous=True)
    pub = rospy.Publisher('/base_to_arm_controller', String, queue_size=25)
    pub1 = rospy.Publisher('/base_to_rvr_arm', String, queue_size=25)
    rospy.Subscriber('/move_group/fake_controller_joint_states', JS, callback)
    rospy.Subscriber('/joy', Joy, callbackjoy)
    rate = rospy.Rate(50) # 10hz
    global flag, msg, plan_flag
    while not rospy.is_shutdown():
        #hello_str = "hello world %s" % rospy.get_time()
        #rospy.loginfo(hello_str)
        if flag and plan_flag:  
            for i in range(6):
                if i==1:
                    continue
                if i<3:
                    pub1.publish(msg[5-i])
                else:
                    pub.publish(msg[5-i])
                rate.sleep()
            flag = False
            plan_flag = False
       
        

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
        
