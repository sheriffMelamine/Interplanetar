#!/usr/bin/env python

import rospy
import sys
import moveit_commander

from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped as Poses
from sensor_msgs.msg import Joy
from tf.transformations import euler_from_quaternion as efq
from tf.transformations import quaternion_from_euler as qfe



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

msg2 = Poses()
msg3 = Poses()

def callback(data):
    
    global msg2
    
    msg2.pose.position.x = data.axes[myjoy["RX"]]*.01
    msg2.pose.position.y = data.axes[myjoy["RY"]]*.01
    msg2.pose.position.z = data.axes[myjoy["LT"]]*.005-data.axes[myjoy["RT"]]*.005
    
    msg3.pose.position.x = data.axes[myjoy["EW"]]*.05
    msg3.pose.position.y = data.axes[myjoy["NS"]]*.05
    
    
    

def talker():
    
    global msg2,msg3
    i=0
    
    moveit_commander.roscpp_initialize(sys.argv)
    rospy.init_node('prochesta_joy_cmd',anonymous=True)
    
    move_group = moveit_commander.MoveGroupCommander("arm")
    rospy.Subscriber('/joy',Joy, callback)
    rate = rospy.Rate(50)
    
    while not rospy.is_shutdown():
        if i==0:
            current_pose = move_group.get_current_pose().pose
        
        current_pose.position.x -= msg2.pose.position.x
        current_pose.position.y += msg2.pose.position.y
        current_pose.position.z += msg2.pose.position.z
        
        orientation = [current_pose.orientation.x, current_pose.orientation.y, current_pose.orientation.z, current_pose.orientation.w]
        (r,p,y) = efq(orientation)
        y += msg3.pose.position.x
        r += msg3.pose.position.y 
        (current_pose.orientation.x,current_pose.orientation.y,current_pose.orientation.z,current_pose.orientation.w)=qfe(r,p,y)
        
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
        
