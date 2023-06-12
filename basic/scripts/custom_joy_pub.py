#!/usr/bin/env python

import rospy

from std_msgs.msg import String
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy


myjoy = {
    "MAC": rospy.get_param("/myjoy/device/MAC"),

    "LX": rospy.get_param("/myjoy/axis/LX"),
    "LY": rospy.get_param("/myjoy/axis/LY"),
    "RX": rospy.get_param("/myjoy/axis/RX"),
    "RY": rospy.get_param("/myjoy/axis/RY"),
    "LT": rospy.get_param("/myjoy/axis/LT"),
    "RT": rospy.get_param("/myjoy/axis/RT"),
    "NS": rospy.get_param("/myjoy/axis/NS"),
    "EW": rospy.get_param("/myjoy/axis/EW"),
    
    "X": rospy.get_param("/myjoy/button/X"),
    "Y": rospy.get_param("/myjoy/button/Y"),
    "A": rospy.get_param("/myjoy/button/A"),
    "B": rospy.get_param("/myjoy/button/B"),
    "START": rospy.get_param("/myjoy/button/START"),
    "SELECT": rospy.get_param("/myjoy/button/SELECT"),
    "LB": rospy.get_param("/myjoy/button/LB"),
    "RB": rospy.get_param("/myjoy/button/RB"),
    "LP": rospy.get_param("/myjoy/button/LP"),
    "RP": rospy.get_param("/myjoy/button/RP"),
}

msg1 = Twist()

flag_l = False
flag_a = False


btns = ["B","X","A","Y","RB","START"]
cmds_1 = ["R1","R2","G1","G2","X1","Z0"]
cmds_0 = ["R0","R0","G0","G0","X0","Z0"]

flags = [False]*len(btns)
old = [0]*len(btns)

def callback(data):
    global msg1,old,btns,flags, flag_l, flag_a
    
    if msg1.linear.x == 0.8*data.axes[myjoy["LY"]]:
        flag_l = False
    else:
        flag_l = True
        msg1.linear.x = 0.8*data.axes[myjoy["LY"]]
        
    if msg1.angular.z == 0.8*data.axes[myjoy["LX"]]:
        flag_a = False
    else:
        flag_a = True
        msg1.angular.z = 0.8*data.axes[myjoy["LX"]]
        
    for i in range(len(btns)):
        if data.buttons[myjoy[btns[i]]]==old[i]:
            flags[i]=False
        else:
            flags[i]=True
            old[i]=data.buttons[myjoy[btns[i]]]
            
 

def talker():
    
    global msg1,flags,old,cmds_0,cmds_1,cmdx_r,cmdx_l,cmdx_0,oldact,flagx,flagy,flagp,flag_l,flag_a
    
    rospy.init_node('prochesta_joy_pub',anonymous=True)
    pub0 = rospy.Publisher('/cmd_vel',Twist, queue_size=25)
    pub1 = rospy.Publisher('/base_to_rvr_arm',String, queue_size=25)
    rospy.Subscriber('/joy',Joy, callback)
    rate = rospy.Rate(50)
    
    while not rospy.is_shutdown():
        
        if flag_l is True or flag_a is True:
            pub0.publish(msg1)
            flag_l = False
            flag_a = False
        for i in range(len(btns)):
            if flags[i]==True:
                flags[i]=False
                if old[i]:
                    pub1.publish(String(cmds_1[i]))
                else:
                    pub1.publish(String(cmds_0[i]))
     
        rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
        
