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

ylim = [10,175]
plim = [5,130]

msg1 = Twist()

flags = [False,False,False,False,False,False,False]
flagx = [False,False,False]
flagp = False
flagy = False

oldact = [0,0,0]
old = [0,0,0,0,0,0,0]

btns = ["X","Y","A","B","RB"]
cmds_1 = ["R1","R2","G1","G2","X1"]
cmds_0 = ["R0","R0","G0","G0","X0"]
cmdx_r = ["B500","E500","S500"]
cmdx_l = ["B600","E600","S600"]
cmdx_0 = ["B700","E700","S700"]

oldy = (ylim[0]+ylim[1])//2
oldp = (plim[0]+plim[1])//2

def callback(data):
    global msg1,flags,old,btns,oldact,flagx,oldy,oldp,ylim,plim,flagy,flagp
    
    msg1.linear.x = data.axes[myjoy["LY"]]
    msg1.angular.z = data.axes[myjoy["LX"]]
    
    for i in range(len(btns)):
        if data.buttons[myjoy[btns[i]]]==old[i]:
            flags[i]=False
        else:
            flags[i]=True
            old[i]=data.buttons[myjoy[btns[i]]]
            
    if data.axes[myjoy["RX"]]>0.:
        if oldact[0]==1:
            flagx[0]=False
        else:
            flagx[0]=True
            oldact[0]=1  
    elif data.axes[myjoy["RX"]]<0.:
        if oldact[0]==-1:
            flagx[0]=False
        else:
            flagx[0]=True
            oldact[0]=-1
    else:
        if oldact[0]==0:
            flagx[0]=False
        else:
            flagx[0]=True
            oldact[0]=0
            
    if data.axes[myjoy["RY"]]>0.:
        if oldact[1]==1:
            flagx[1]=False
        else:
            flagx[1]=True
            oldact[1]=1  
    elif data.axes[myjoy["RY"]]<0.:
        if oldact[1]==-1:
            flagx[1]=False
        else:
            flagx[1]=True
            oldact[1]=-1
    else:
        if oldact[1]==0:
            flagx[1]=False
        else:
            flagx[1]=True
            oldact[1]=0
    
    if data.axes[myjoy["LT"]]-data.axes[myjoy["RT"]]>0.:
        if oldact[2]==1:
            flagx[2]=False
        else:
            flagx[2]=True
            oldact[2]=1  
    elif data.axes[myjoy["LT"]]-data.axes[myjoy["RT"]]<0.:
        if oldact[2]==-1:
            flagx[2]=False
        else:
            flagx[2]=True
            oldact[2]=-1  
    else:
        if oldact[2]==0:
            flagx[2]=False
        else:
            flagx[2]=True
            oldact[2]=0
    
    if data.axes[myjoy["NS"]]>0. and oldp+3>plim[0]:
        oldp -= 3
        flagp = True
    elif data.axes[myjoy["NS"]]<0. and oldp-3<plim[1]:
        oldp += 3
        flagp = True
    else:
        flagp = False
    
    
    if data.axes[myjoy["EW"]]>0. and oldy+3>ylim[0]:
        oldy -= 3
        flagy = True
    elif data.axes[myjoy["EW"]]<0. and oldy-3<ylim[1]:
        oldy += 3
        flagy = True
    else:
        flagy = False
    

def talker():
    
    global msg1,flags,old,cmds_0,cmds_1,cmdx_r,cmdx_l,cmdx_0,oldact,flagx,flagy,flagp
    
    rospy.init_node('prochesta_joy_pub',anonymous=True)
    pub0 = rospy.Publisher('/cmd_vel',Twist, queue_size=25)
    pub1 = rospy.Publisher('/base_to_rvr_arm',String, queue_size=25)
    rospy.Subscriber('/joy',Joy, callback)
    rate = rospy.Rate(50)
    
    while not rospy.is_shutdown():
        
        pub0.publish(msg1)
        for i in range(len(btns)):
            if flags[i]==True:
                flags[i]=False
                if old[i]:
                    pub1.publish(String(cmds_1[i]))
                else:
                    pub1.publish(String(cmds_0[i]))
        for i in range(3):
            if flagx[i]==True:
                flagx[i]=False
                if oldact[i]==-1:
                    pub1.publish(String(cmdx_l[i]))
                elif oldact[i]==1:
                    pub1.publish(String(cmdx_r[i]))
                else:
                    pub1.publish(String(cmdx_0[i]))
        if flagy:
            pub1.publish(String("Y"+str(oldy)))
            flagy=False
            
        if flagp:
            pub1.publish(String("P"+str(oldp)))
            flagp=False
        
        rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
        
