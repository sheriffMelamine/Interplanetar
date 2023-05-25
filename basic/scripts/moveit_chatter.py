#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from sensor_msgs.msg import JointState as JS
from sensor_msgs.msg import Joy
from math import pi

def map_range(x,a,b,c,d):
    return (x-a)*(d-c)/(b-a) + c 

anglemin = [5.,140.,172.,5.,10.]
anglemax = [245.,200.,210.,130.,175.]
urdfmin = [-2.*pi/3.,-1.,-0.5,1.2217,.8727,0.]
urdfmax = [2.*pi/3.,0.,0.7837,-1.2217,-.8727,0.]

flag = False
msg = [""]
joint=["B","S","E","P","Y","R"]

#Change this button only for different joystick
button = 6
plan_flag = False
oldbtn = 0

def callback(data):
    global flag,msg
    flag=True
   
    for i in range(5):
        #rospy.loginfo(rospy.get_caller_id() + "I heard %s is  %f",data.name[i],data.position[i])
        msg.append(joint[i]+str((int(round(map_range(data.position[i],urdfmin[i],urdfmax[i],anglemin[i],anglemax[i]))))%360))

def callbackjoy(data):
    global oldbtn, button, plan_flag
    if data.buttons[button]==0 and oldbtn==1:
        plan_flag = True
    oldbtn = data.buttons[button]
    
    
def talker():
    rospy.init_node('moveit_workaround', anonymous=True)
    pub = rospy.Publisher('/base_to_arm_controller', String, queue_size=25)
    rospy.Subscriber('/move_group/fake_controller_joint_states', JS, callback)
    rospy.Subscriber('/joy', Joy, callbackjoy)
    rate = rospy.Rate(50) # 10hz
    global flag, msg, plan_flag
    while not rospy.is_shutdown():
        #hello_str = "hello world %s" % rospy.get_time()
        #rospy.loginfo(hello_str)
        if flag and plan_flag:  
            for i in range(5):
                if len(msg)>2:  
                    pub.publish(msg.pop(1))
                    rate.sleep()
            flag = False
            plan_flag = False
       
        

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
        
