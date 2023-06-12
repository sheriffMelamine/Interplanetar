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



ylim = [10,175]
plim = [5,230]

msg1 = Twist()

btns = ["B","X","A","Y","RB","START"]
cmds_1 = ["R1","R2","G1","G2","X1","Z0"]
cmds_0 = ["R0","R0","G0","G0","X0","Z0"]
cmdx_r = ["B500","S500","E500"]
cmdx_l = ["B600","S600","E600"]
cmdx_0 = ["B700","S700","E700"]

flag_l = False
flag_a = False
flags = [False]*len(btns)
flagx = [False]*len(cmdx_0)
flagp = False
flagy = False

oldact = [0]*len(cmdx_0)
old = [0]*len(btns)

oldy = (ylim[0]+ylim[1])//2
oldp = (plim[0]+plim[1])//2

def callback(data):
    global msg1,flags,old,btns,oldact,flagx,oldy,oldp,ylim,plim,flagy,flagp, flag_l, flag_a
    turbo = data.buttons[myjoy["SELECT"]]
    brek = data.buttons[myjoy["LB"]]
    
    if msg1.linear.x == (1.-0.3*turbo)*data.axes[myjoy["LY"]]:
        flag_l = False
    else:
        flag_l = True
        msg1.linear.x = (1.-0.3*turbo)*data.axes[myjoy["LY"]]
        
    if msg1.angular.z == -(1.-0.3*turbo)*data.axes[myjoy["LX"]]:
        flag_a = False
    else:
        flag_a = True
        msg1.angular.z = -(1.-0.3*turbo)*data.axes[myjoy["LX"]]
    
    if brek:    
        msg1.linear.z = -1.
    else:
        msg1.linear.z = 0.
        
    for i in range(len(btns)):
        if data.buttons[myjoy[btns[i]]]==old[i]:
            flags[i]=False
        else:
            flags[i]=True
            old[i]=data.buttons[myjoy[btns[i]]]
            
    if data.axes[myjoy["RX"]]>0.2:
        if oldact[0]==1:
            flagx[0]=False
        else:
            flagx[0]=True
            oldact[0]=1  
    elif data.axes[myjoy["RX"]]<-0.2:
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
            
    if data.axes[myjoy["RY"]]<-0.2:
        if oldact[1]==1:
            flagx[1]=False
        else:
            flagx[1]=True
            oldact[1]=1  
    elif data.axes[myjoy["RY"]]>0.2:
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
    
    if data.axes[myjoy["LT"]]-data.axes[myjoy["RT"]]>0.2:
        if oldact[2]==1:
            flagx[2]=False
        else:
            flagx[2]=True
            oldact[2]=1  
    elif data.axes[myjoy["LT"]]-data.axes[myjoy["RT"]]<-0.2:
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
    
    if data.axes[myjoy["NS"]]>0. and oldp>plim[0]+3:
        oldp -= 3
        flagp = True
    elif data.axes[myjoy["NS"]]<0. and oldp<plim[1]-3:
        oldp += 3
        flagp = True
    else:
        flagp = False
    
    
    if data.axes[myjoy["EW"]]>0. and oldy>ylim[0]+3:
        oldy -= 3
        flagy = True
    elif data.axes[myjoy["EW"]]<0. and oldy<ylim[1]-3:
        oldy += 3
        flagy = True
    else:
        flagy = False
    

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
        
