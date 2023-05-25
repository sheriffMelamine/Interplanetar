#!/usr/bin/env python

import rospy
from sensor_msgs.msg import Joy

maxvel=0.

def callback(data):
    global maxvel
    x = data.axes[0]
    z = data.axes[1]
    maxvel=x+z if x+z>maxvel else maxvel
    rospy.loginfo("%f,%f,%f",x,z,1./maxvel)

def talker():
    
    rospy.init_node('test_joy', anonymous=True)
    rospy.Subscriber('/joy', Joy, callback)
   
    rospy.spin()

if __name__ == '__main__':
    talker()
   
        
