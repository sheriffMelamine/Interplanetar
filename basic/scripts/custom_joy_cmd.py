#!/usr/bin/env python

import rospy
import moveit_commander
import sys

from std_msgs.msg import Empty
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped as Poses
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy

myjoy = {
    "MAC": "CC:15:79:90:63:25",

    "LX": 0,
    "LY": 1,
    "RX": 2,
    "RY": 3,
    "LT": 5,
    "RT": 4,
    "NS": 7,
    "EW": 6,
    
    "X": 3,
    "Y": 4,
    "A": 0,
    "B": 1,
    "START": 11,
    "SELECT": 10,
    "LB": 6,
    "RB": 7,
    "LP": 13,
    "RP": 14
}

msg2 = Poses()

def callback(data):
    
    global msg2
    
    msg2.pose.position.x = data.axes[myjoy["RX"]]*.01
    msg2.pose.position.y = data.axes[myjoy["RY"]]*.01
    msg2.pose.position.z = data.axes[myjoy["LT"]]*.005-data.axes[myjoy["RT"]]*.005
    
    
    

def talker():
    
    global msg2
    i=0
    
    moveit_commander.roscpp_initialize(sys.argv)
    rospy.init_node('prochesta_joy_cmd',anonymous=True)
    
    move_group = moveit_commander.MoveGroupCommander("arm")
    rospy.Subscriber('/joy',Joy, callback)
    rate = rospy.Rate(50)
    
    while not rospy.is_shutdown():
        if i==0:
            current_pose = move_group.get_current_pose().pose
        
        current_pose.position.x += msg2.pose.position.x
        current_pose.position.y += msg2.pose.position.y
        current_pose.position.z += msg2.pose.position.z
        
        i+=1
        
        if i==4:
            move_group.set_pose_target(current_pose)
            move_group.go(wait=True)
        if i==8:   
            i=0
        
if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
        
