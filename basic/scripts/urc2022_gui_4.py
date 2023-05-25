#! /usr/bin/python3

#IMPORT DEPENDENCIES------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

import rospy
import sys

from std_msgs.msg import String
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image as Image_sub

from cv_bridge import CvBridge # Package to convert between ROS and OpenCV Images

from kivymd.app import MDApp
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.button import MDRectangleFlatButton

from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.tabbedpanel import TabbedPanel

from kivy.app import App

from kivy.graphics.texture import Texture
from kivy.clock import Clock

from kivymd.uix.label import MDLabel
from kivy.uix.image import Image
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager

from kivy.core.window import Window
from kivy.uix.widget import Widget

from kivy.base import runTouchApp

import cv2
import numpy as np 
import time
from functools import partial
#IMPORT DEPENDENCIES------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#SOME CONTROL PARAMETERS & VARIABLES--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

current_frame_1 = cv2.imread("src/basic/images/stby.png") #when there is no feed connected, this image is shown
current_frame_2 = cv2.imread("src/basic/images/stby.png") #when there is no feed connected, this image is shown
current_frame_3 = cv2.imread("src/basic/images/stby.png") #when there is no feed connected, this image is shown
current_frame_4 = cv2.imread("src/basic/images/stby.png") #when there is no feed connected, this image is shown

toggle_1 = 0
toggle_2 = 0
toggle_3 = 0
toggle_4 = 0

feed_num = 1
speed = 0

#OTHER GLOBAL VARIABLES ARE DECLARED ON LINE 514

#SOME CONTROL PARAMETERS & VARIABLES--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#KEYBOARD-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class MyKeyboardListener(Widget):

    def __init__(self, **kwargs):
        super(MyKeyboardListener, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')
        if self._keyboard.widget:
            # If it exists, this widget is a VKeyboard object which you can use
            # to change the keyboard layout.
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down, on_key_up=self._on_keyboard_up)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down, on_key_up=self._on_keyboard_up)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'w':#forward
            msg = Twist()
            msg.linear.x = speed/100
            vel_pub.publish(msg)
            #output = 1
            #command = "M"+str(output)
            #move_pub.publish(command)
        if keycode[1] == 's':#back
            #print(args)
            msg = Twist()
            msg.linear.x = -speed/100
            vel_pub.publish(msg)
            #output = 2
            #command = "M"+str(output)
            #move_pub.publish(command)
        if keycode[1] == 'a':#left
            #print(args)
            msg = Twist()
            msg.angular.z = speed/100
            vel_pub.publish(msg)
            #output = 3
            #command = "M"+str(output)
            #move_pub.publish(command)
        if keycode[1] == 'd': #right
            #print(args)
            msg = Twist()
            msg.angular.z = -speed/100
            vel_pub.publish(msg)
            #output = 4
            #command = "M"+str(output)
            #move_pub.publish(command)
        if keycode[1] == 'f':
            #print(args)
            msg = Twist()
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            vel_pub.publish(msg)
            #output = 0
            #command = "M"+str(output)
            #move_pub.publish(command)
            output = 0
            command = "Z"+str(output)
            arm_pub.publish(command)
            sci_pub.publish(command)
            stat_pub.publish(command)

        # If we hit escape, release the keyboard
        if keycode[1] == 'escape':
            print('Press ESC Again to Exit')
            keyboard.release()

        return True

    def _on_keyboard_up(self, keyboard, keycode, *args):
        if keycode[1] == 'w':
            msg = Twist()
            msg.linear.x = 0.0
            msg.angular.x = 0.0
            vel_pub.publish(msg)
            #output = 0
            #command = "M"+str(output)
            #move_pub.publish(command)
        if keycode[1] == 's':
            msg = Twist()
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            vel_pub.publish(msg)
            #output = 0
            #command = "M"+str(output)
            #move_pub.publish(command)
        if keycode[1] == 'a':
            msg = Twist()
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            vel_pub.publish(msg)
            #output = 0
            #command = "M"+str(output)
            #move_pub.publish(command)
        if keycode[1] == 'd':
            msg = Twist()
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            vel_pub.publish(msg)
            #output = 0
            #command = "M"+str(output)
            #move_pub.publish(command)

        return True

    pass

#KEYBOARD-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



class InterplaneterUIApp(MDApp):
    def on_start(self, **kwargs):
        #camera feed subcribers
        try:
            rospy.Subscriber('camera/color/image_raw', Image_sub, callback_img_1)
        except:
            print("Failed to set up main camera subscriber")
        try:
            rospy.Subscriber('usb_cam_1/image_raw', Image_sub, callback_img_2)
        except:
            print("Failed to set up arm camera subscriber")
        try:
            rospy.Subscriber('usb_cam_2/image_raw', Image_sub, callback_img_3)
        except:
            print("Failed to set up science camera subscriber")
        try:
            rospy.Subscriber('video_frames', Image_sub, callback_img_4)
        except:
            print("Failed to set up microscope camera subscriber")

        #other subscribers
        try:
            rospy.Subscriber("rvr_to_base_move", String, callback_move)
        except:
            print("Failed to set up move subscriber")  
        try:
            rospy.Subscriber("rvr_to_base_arm", String, callback_arm)
        except:
            print("Failed to set up arm subscriber")  
        try:
            rospy.Subscriber("rvr_to_base_sci", String, callback_sci)
        except:
            print("Failed to set up science subscriber")  
        try:
            rospy.Subscriber("rvr_to_base_stat", String, callback_stat)
        except:
            print("Failed to set up status subscriber")            

        runTouchApp(MyKeyboardListener())
        

    def build(self):
        layout = MDFloatLayout()
        self.command = "nothing" #declaring an internal variable

        #static text and background--------------------------------------------------------------------------------------------------------------------------

        self.image = Image(source="src/basic/images/urc_gui.png", size_hint = (1.,1.), pos_hint={'center_x': 0.5, 'center_y': 0.5}, allow_stretch = 1,keep_ratio=0)
        layout.add_widget(self.image)

        #self.heading_text = Label(text='Prochesta V1.0', pos_hint={'center_x': .5, 'center_y': .975}, size_hint=(0.4,0.4),font_size = 40)
        #layout.add_widget(self.heading_text)

        self.cam_text = Label(text='Camera Feed', pos_hint={'center_x': .26, 'center_y': .9}, size_hint=(0.4,0.4),font_size = 30)
        layout.add_widget(self.cam_text)

        self.sci_text = Label(text='-----  Science Module Controls  ----', pos_hint={'center_x': .26, 'center_y': .05}, size_hint=(0.4,0.4),font_size = 30)
        layout.add_widget(self.sci_text)

        self.arm_text = Label(text='-----  Arm Controls  -----', pos_hint={'center_x': .74, 'center_y': .85}, size_hint=(0.4,0.4),font_size = 30)
        layout.add_widget(self.arm_text)

        self.move_text = Label(text='-----  Other Controls  -----', pos_hint={'center_x': .74, 'center_y': .05}, size_hint=(0.4,0.4),font_size = 30)
        layout.add_widget(self.move_text)

        #static text and background--------------------------------------------------------------------------------------------------------------------------

        #the video feed--------------------------------------------------------------------------------------------------------------------------------------

        self.image_feed = Image(size_hint = (0.55,0.55), pos_hint = {"center_x": 0.26,"center_y": 0.6}, allow_stretch = 1)
        layout.add_widget(self.image_feed)

        #the video feed--------------------------------------------------------------------------------------------------------------------------------------

        #arm controls---------------------------------------------------------------------------------

        self.base = Slider(min=0, max=360, value=0, step=1, orientation='horizontal', size_hint = (0.15,0.025), pos_hint = {"center_x": 0.71,"center_y": 0.55-.05})
        self.base.bind(value=self.move_base)
        layout.add_widget(self.base)
        self.base_val = Label(text='0', pos_hint={'center_x': .795, 'center_y': .55-.05}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.base_val)
        self.base_text = Label(text='Base', pos_hint={'center_x': .835, 'center_y': .55-.05}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.base_text)
        self.base_targ = Label(text='X', pos_hint={'center_x': .875, 'center_y': .55-.05}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.base_targ)
        self.base_set_button = MDRectangleFlatButton(line_color="cyan",text_color="white",text="Track", pos_hint={'center_x': .61, 'center_y': .55-.05}, size_hint=(0.01,0.03),font_size = 20)
        self.base_set_button.bind(on_press=self.base_set)
        layout.add_widget(self.base_set_button)
        self.base_left_button = MDRectangleFlatButton(line_color="cyan",text_color="white",text="<-", pos_hint={'center_x': .925, 'center_y': .55-.05}, size_hint=(0.01,0.03),font_size = 20)
        self.base_left_button.bind(on_press=self.base_left)
        self.base_left_button.bind(on_release=self.base_stop)
        layout.add_widget(self.base_left_button)
        self.base_right_button = MDRectangleFlatButton(line_color="cyan",text_color="white",text="->", pos_hint={'center_x': .975, 'center_y': .55-.05}, size_hint=(0.01,0.03),font_size = 20)
        self.base_right_button.bind(on_press=self.base_right)
        self.base_right_button.bind(on_release=self.base_stop)
        layout.add_widget(self.base_right_button)

        self.shoulder = Slider(min=0, max=180, value=0, step=1, orientation='horizontal', size_hint = (0.15,0.025), pos_hint = {"center_x": 0.71,"center_y": 0.6-.05})
        self.shoulder.bind(value=self.move_shoulder)
        layout.add_widget(self.shoulder)
        self.shoulder_val = Label(text='0', pos_hint={'center_x': .795, 'center_y': .6-.05}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.shoulder_val)
        self.shoulder_text = Label(text='Shoulder', pos_hint={'center_x': .835, 'center_y': .6-.05}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.shoulder_text)
        self.shoulder_targ = Label(text='X', pos_hint={'center_x': .875, 'center_y': .6-.05}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.shoulder_targ)
        self.shoulder_set_button = MDRectangleFlatButton(line_color="cyan",text_color="white",text="Track", pos_hint={'center_x': .61, 'center_y': .6-.05}, size_hint=(0.01,0.03),font_size = 20)
        self.shoulder_set_button.bind(on_press=self.shoulder_set)
        layout.add_widget(self.shoulder_set_button)
        self.shoulder_left_button = MDRectangleFlatButton(line_color="cyan",text_color="white",text="<-", pos_hint={'center_x': .925, 'center_y': .6-.05}, size_hint=(0.01,0.03),font_size = 20)
        self.shoulder_left_button.bind(on_press=self.shoulder_left)
        self.shoulder_left_button.bind(on_release=self.shoulder_stop)
        layout.add_widget(self.shoulder_left_button)
        self.shoulder_right_button = MDRectangleFlatButton(line_color="cyan",text_color="white",text="->", pos_hint={'center_x': .975, 'center_y': .6-.05}, size_hint=(0.01,0.03),font_size = 20)
        self.shoulder_right_button.bind(on_press=self.shoulder_right)
        self.shoulder_right_button.bind(on_release=self.shoulder_stop)
        layout.add_widget(self.shoulder_right_button)

        self.elbow = Slider(min=0, max=180, value=0, step=1, orientation='horizontal', size_hint = (0.15,0.025), pos_hint = {"center_x": 0.71,"center_y": 0.65-.05})
        self.elbow.bind(value=self.move_elbow)
        layout.add_widget(self.elbow)
        self.elbow_val = Label(text='0', pos_hint={'center_x': .795, 'center_y': .65-.05}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.elbow_val)
        self.elbow_text = Label(text='Elbow', pos_hint={'center_x': .835, 'center_y': .65-.05}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.elbow_text)
        self.elbow_targ = Label(text='X', pos_hint={'center_x': .875, 'center_y': .65-.05}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.elbow_targ)
        self.elbow_set_button = MDRectangleFlatButton(line_color="cyan",text_color="white",text="Track", pos_hint={'center_x': .61, 'center_y': .65-.05}, size_hint=(0.01,0.03),font_size = 20)
        self.elbow_set_button.bind(on_press=self.elbow_set)
        layout.add_widget(self.elbow_set_button)
        self.elbow_left_button = MDRectangleFlatButton(line_color="cyan",text_color="white",text="<-", pos_hint={'center_x': .925, 'center_y': .65-.05}, size_hint=(0.01,0.03),font_size = 20)
        self.elbow_left_button.bind(on_press=self.elbow_left)
        self.elbow_left_button.bind(on_release=self.elbow_stop)
        layout.add_widget(self.elbow_left_button)
        self.elbow_right_button = MDRectangleFlatButton(line_color="cyan",text_color="white",text="->", pos_hint={'center_x': .975, 'center_y': .65-.05}, size_hint=(0.01,0.03),font_size = 20)
        self.elbow_right_button.bind(on_press=self.elbow_right)
        self.elbow_right_button.bind(on_release=self.elbow_stop)
        layout.add_widget(self.elbow_right_button)

        self.pitch = Slider(min=0, max=270, value=0, step=1, orientation='horizontal', size_hint = (0.15,0.025), pos_hint = {"center_x": 0.71,"center_y": 0.7-.05})
        self.pitch.bind(value=self.move_pitch)
        layout.add_widget(self.pitch)
        self.pitch_val = Label(text='0', pos_hint={'center_x': .795, 'center_y': .7-.05}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.pitch_val)
        self.pitch_text = Label(text='Pitch', pos_hint={'center_x': .835, 'center_y': .7-.05}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.pitch_text)
        self.pitch_targ = Label(text='X', pos_hint={'center_x': .875, 'center_y': .7-.05}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.pitch_targ)

        self.yaw = Slider(min=0, max=270, value=0, step=1, orientation='horizontal', size_hint = (0.15,0.025), pos_hint = {"center_x": 0.71,"center_y": 0.75-.05})
        self.yaw.bind(value=self.move_yaw)
        layout.add_widget(self.yaw)
        self.yaw_val = Label(text='0', pos_hint={'center_x': .795, 'center_y': .75-.05}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.yaw_val)
        self.yaw_text = Label(text='Yaw', pos_hint={'center_x': .835, 'center_y': .75-.05}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.yaw_text)
        self.yaw_targ = Label(text='X', pos_hint={'center_x': .875, 'center_y': .75-.05}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.yaw_targ)

        self.roll_cw_button = MDRectangleFlatButton(line_color="cyan",text_color="white",text="Roll CW", pos_hint={'center_x': .71, 'center_y': .8-.05}, size_hint=(0.05,0.05),font_size = 20)
        self.roll_cw_button.bind(on_press=self.roll_cw)
        self.roll_cw_button.bind(on_release=self.roll_stop)
        layout.add_widget(self.roll_cw_button)
        self.roll_ccw_button = MDRectangleFlatButton(line_color="cyan",text_color="white",text="Roll CCW", pos_hint={'center_x': .65, 'center_y': .8-.05}, size_hint=(0.05,0.05),font_size = 20)
        self.roll_ccw_button.bind(on_press=self.roll_ccw)
        self.roll_ccw_button.bind(on_release=self.roll_stop)
        layout.add_widget(self.roll_ccw_button)

        self.grip_open_button = MDRectangleFlatButton(line_color="cyan",text_color="white",text="Grip Open", pos_hint={'center_x': .77, 'center_y': .8-.05}, size_hint=(0.05,0.05),font_size = 20)
        self.grip_open_button.bind(on_press=self.grip_open)
        self.grip_open_button.bind(on_release=self.grip_stop)
        layout.add_widget(self.grip_open_button)
        self.grip_close_button = MDRectangleFlatButton(line_color="cyan",text_color="white",text="Grip Close", pos_hint={'center_x': .83, 'center_y': .8-.05}, size_hint=(0.05,0.05),font_size = 20)
        self.grip_close_button.bind(on_press=self.grip_close)
        self.grip_close_button.bind(on_release=self.grip_stop)
        layout.add_widget(self.grip_close_button)

        self.press_a_button = MDRectangleFlatButton(line_color="cyan",text_color="white",text="Press A", pos_hint={'center_x': .89, 'center_y': .82-.05}, size_hint=(0.025,0.025),font_size = 15)
        self.press_a_button.bind(on_press=self.press_a)
        self.press_a_button.bind(on_release=self.press_s)
        layout.add_widget(self.press_a_button)
        self.press_b_button = MDRectangleFlatButton(line_color="cyan",text_color="white",text="Press B", pos_hint={'center_x': .89, 'center_y': .78-.05}, size_hint=(0.025,0.025),font_size = 15)
        self.press_b_button.bind(on_press=self.press_b)
        self.press_b_button.bind(on_release=self.press_s)
        layout.add_widget(self.press_b_button)
        
        self.screw_cw_button = MDRectangleFlatButton(line_color="cyan",text_color="white",text="Screw CW", pos_hint={'center_x': .59, 'center_y': .82-.05}, size_hint=(0.025,0.025),font_size = 15)
        self.screw_cw_button.bind(on_press=self.screw_cw)
        self.screw_cw_button.bind(on_release=self.screw_stop)
        layout.add_widget(self.screw_cw_button)
        self.screw_ccw_button = MDRectangleFlatButton(line_color="cyan",text_color="white",text="Screw CCW", pos_hint={'center_x': .59, 'center_y': .78-.05}, size_hint=(0.025,0.025),font_size = 15)
        self.screw_ccw_button.bind(on_press=self.screw_ccw)
        self.screw_ccw_button.bind(on_release=self.screw_stop)
        layout.add_widget(self.screw_ccw_button)

        self.activate_arm = Slider(min=0, max=1, value=0, step=1, orientation='horizontal', size_hint = (0.05,0.05), pos_hint = {"center_x": 0.95,"center_y": 0.8-.05})
        self.activate_arm.bind(value=self.activate_arm_on_value)
        layout.add_widget(self.activate_arm)
        self.activate_arm_val = Label(text='Locked', pos_hint={'center_x': .95, 'center_y': .77-.05}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.activate_arm_val)
        self.activate_arm_text = Label(text='Activate Arm', pos_hint={'center_x': .95, 'center_y': .79}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.activate_arm_text)

        self.mux_val = Label(text='X', pos_hint={'center_x': .95, 'center_y': .7-.05}, size_hint=(0.4,0.4),font_size = 15)
        layout.add_widget(self.mux_val)
        self.mux_text = Label(text='MUX', pos_hint={'center_x': .95, 'center_y': .725-.05}, size_hint=(0.4,0.4),font_size = 15)
        layout.add_widget(self.mux_text)


        

        self.arm_info = Label(text='Press F for Emergency Stop. Activate the Arm before pushing buttons and pulling sliders', pos_hint={'center_x': .79, 'center_y': .425}, size_hint=(0.4,0.4),font_size = 15)
        layout.add_widget(self.arm_info)


        #arm controls---------------------------------------------------------------------------------

        #science module---------------------------------------------------------------------------------

        
        for i in range(6):
            self.pump_button = MDRectangleFlatButton(line_color="cyan",text_color="white",text="Pump "+str(int(i+1)), pos_hint={'center_x': .0925+i*0.07, 'center_y': .260}, size_hint=(0.06,0.08),font_size = 20)
            self.pump_button.bind(on_press=partial(self.pump,i))
            self.pump_button.bind(on_release=partial(self.pump_stop,i))
            layout.add_widget(self.pump_button)
        
        direction = ["Left","Right"]
        rails = ["Top Rail ","Side Rail "]   
        for i in range(2):
            for j in range(2):
                self.motor_button = MDRectangleFlatButton(line_color="cyan",text_color="white",text=rails[i]+direction[j], pos_hint={'center_x': .1125+j*0.1+i*0.21, 'center_y': .160}, size_hint=(0.09,0.08),font_size = 20)
                self.motor_button.bind(on_press=partial(self.motor,3*i+j+1))
                self.motor_button.bind(on_release=partial(self.motor,3*i))
                layout.add_widget(self.motor_button)
                
            
   
        #self.drill_down_button = MDRectangleFlatButton(line_color="cyan",text_color="white",text="S1 Down", pos_hint={'center_x': .175, 'center_y': .150}, size_hint=(0.05,0.05),font_size = 20)
        #self.drill_down_button.bind(on_press=self.drill_down)
        #self.drill_down_button.bind(on_release=self.drill_stop)
        #layout.add_widget(self.drill_down_button)
        #self.drill_up_button = MDRectangleFlatButton(line_color="cyan",text_color="white",text="S2 Up", pos_hint={'center_x': .23, 'center_y': .150}, size_hint=(0.05,0.05),font_size = 20)
        #self.drill_up_button.bind(on_press=self.drill_up)
        #self.drill_up_button.bind(on_release=self.drill_stop)
        #layout.add_widget(self.drill_up_button)
        #self.drill_cw_button = MDRectangleFlatButton(line_color="cyan",text_color="white",text="S1 Down", pos_hint={'center_x': .285, 'center_y': .150}, size_hint=(0.05,0.05),font_size = 20)
        #self.drill_cw_button.bind(on_press=self.drill_cw)
        #self.drill_cw_button.bind(on_release=self.drill_spin_stop)
        #layout.add_widget(self.drill_cw_button)
        #self.drill_ccw_button = MDRectangleFlatButton(line_color="cyan",text_color="white",text="S2 Up", pos_hint={'center_x': .34, 'center_y': .150}, size_hint=(0.05,0.05),font_size = 20)
        #self.drill_ccw_button.bind(on_press=self.drill_ccw)
        #self.drill_ccw_button.bind(on_release=self.drill_spin_stop)
        #layout.add_widget(self.drill_ccw_button)
        
        

        #self.sci_sensor_text_temp=Label(text='Weight (gms)', pos_hint={'center_x': .46, 'center_y': .2}, size_hint=(0.4,0.8),font_size = 20)
        #layout.add_widget(self.sci_sensor_text_temp)
        #self.sci_sensor_text_moist=Label(text='27.1', pos_hint={'center_x': .46, 'center_y': .15}, size_hint=(0.4,0.8),font_size = 20)
        #layout.add_widget(self.sci_sensor_text_moist)

        #self.sci_sensor_text_1=Label(text='X', pos_hint={'center_x': .49, 'center_y': .175}, size_hint=(0.4,0.8),font_size = 20)
        #layout.add_widget(self.sci_sensor_text_1)
        #self.sci_sensor_text_2=Label(text='X', pos_hint={'center_x': .49, 'center_y': .15}, size_hint=(0.4,0.8),font_size = 20)
        #layout.add_widget(self.sci_sensor_text_2)
        #self.sci_sensor_text_3=Label(text='X', pos_hint={'center_x': .49, 'center_y': .125}, size_hint=(0.4,0.8),font_size = 20)
        #layout.add_widget(self.sci_sensor_text_3)
        

        #self.rc_text=Label(text='Reaction Chamber', pos_hint={'center_x': .45, 'center_y': .3}, size_hint=(0.4,0.4),font_size = 20)
        #layout.add_widget(self.rc_text)
        #self.rc_spin_button = MDRectangleFlatButton(line_color="cyan",text_color="white",text="Spinning", pos_hint={'center_x': .42, 'center_y': .250}, size_hint=(0.05,0.05),font_size = 20)
        #self.rc_spin_button.bind(on_press=self.rc_spin)
        #self.rc_spin_button.bind(on_release=self.rc_stop)
        #layout.add_widget(self.rc_spin_button)
        #self.rc_step_button = MDRectangleFlatButton(line_color="cyan",text_color="white",text="Stepping", pos_hint={'center_x': .48, 'center_y': .25}, size_hint=(0.05,0.05),font_size = 20)
        #self.rc_step_button.bind(on_press=self.rc_step)
        #self.rc_step_button.bind(on_release=self.rc_stop)
        #layout.add_widget(self.rc_step_button)
        
        
        self.sci_info = Label(text='Press F for Emergency Stop', pos_hint={'center_x': .26, 'center_y': .1}, size_hint=(0.4,0.4),font_size = 15)
        layout.add_widget(self.sci_info)

        #science module---------------------------------------------------------------------------------

        #other controls---------------------------------------------------------------------------------
        
        self.move_slider = Slider(min=0, max=100, value=0, step=1, orientation='horizontal', size_hint = (0.15,0.025), pos_hint = {"center_x": 0.74,"center_y": 0.1})
        self.move_slider .bind(value=self.move_slider_on_value)
        layout.add_widget(self.move_slider)
        self.move_slider_val = Label(text='0', pos_hint={'center_x': .83, 'center_y': .1}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.move_slider_val)
        self.move_slider_text = Label(text='Rover Speed', pos_hint={'center_x': .63, 'center_y': .1}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.move_slider_text)

        self.move_info = Label(text='Movement  Keys: W - forward, S - reverse, A - left, D - right, F - stop', pos_hint={'center_x': .70, 'center_y': .15}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.move_info)

        self.cam_feed_slider = Slider(min=1, max=4, value=1, step=1, orientation='horizontal', size_hint = (0.1,0.025), pos_hint = {"center_x": 0.74,"center_y": 0.2})
        self.cam_feed_slider .bind(value=self.cam_feed_slider_on_value)
        layout.add_widget(self.cam_feed_slider)
        self.cam_feed_slider_val = Label(text='Main Cam', pos_hint={'center_x': .835, 'center_y': .2}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.cam_feed_slider_val)
        self.cam_feed_slider_text = Label(text='Camera Feed', pos_hint={'center_x': .625, 'center_y': .2}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.cam_feed_slider_text)

        self.batt_1_info = Label(text='Battery 1 Status:               V               A', pos_hint={'center_x': .74, 'center_y': .325}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.batt_1_info)
        self.batt_2_info = Label(text='Battery 2 Status:               V               A', pos_hint={'center_x': .74, 'center_y': .3}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.batt_2_info)
        self.batt_3_info = Label(text='Battery 3 Status:               V               A', pos_hint={'center_x': .74, 'center_y': .275}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.batt_3_info)
        self.batt_4_info = Label(text='Battery 4 Status:               V               A', pos_hint={'center_x': .74, 'center_y': .25}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.batt_4_info)

        self.batt_1_i = Label(text='X', pos_hint={'center_x': .8, 'center_y': .325}, size_hint=(0.4,0.4),font_size = 20)
        #layout.add_widget(self.batt_1_i)
        self.batt_1_v = Label(text='X', pos_hint={'center_x': .75, 'center_y': .325}, size_hint=(0.4,0.4),font_size = 20)
        #layout.add_widget(self.batt_1_v)

        self.batt_2_i = Label(text='X', pos_hint={'center_x': .8, 'center_y': .3}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.batt_2_i)
        self.batt_2_v = Label(text='X', pos_hint={'center_x': .75, 'center_y': .3}, size_hint=(0.4,0.4),font_size = 20)
        layout.add_widget(self.batt_2_v)

        self.batt_3_i = Label(text='X', pos_hint={'center_x': .8, 'center_y': .275}, size_hint=(0.4,0.4),font_size = 20)
        #layout.add_widget(self.batt_3_i)
        self.batt_3_v = Label(text='X', pos_hint={'center_x': .75, 'center_y': .275}, size_hint=(0.4,0.4),font_size = 20)
        #layout.add_widget(self.batt_3_v)

        self.batt_4_i = Label(text='X', pos_hint={'center_x': .8, 'center_y': .25}, size_hint=(0.4,0.4),font_size = 20)
        #layout.add_widget(self.batt_4_i)
        self.batt_4_v = Label(text='X', pos_hint={'center_x': .75, 'center_y': .25}, size_hint=(0.4,0.4),font_size = 20)
        #layout.add_widget(self.batt_4_v)


        #other controls---------------------------------------------------------------------------------


        #timed events-----------------------------------------------------------------------------------

        Clock.schedule_interval(self.timed_events, 1.0/50.0)

        #timed events-----------------------------------------------------------------------------------

        return layout


    #the video feed functions--------------------------------------------------------------------------------------------------------------------------------------

    #the video feed functions--------------------------------------------------------------------------------------------------------------------------------------
    

    #arm control functions---------------------------------------------------------------------------------

    def move_base(self, instance, value):
        self.command = 'B' + str(int(value))
        self.base_val.text = str(value)
        arm_pub.publish(self.command)
    def base_set(self, *args):
        self.command = 'B400'
        arm_pub.publish(self.command)
    def base_left(self, *args):
        self.command = 'B500'
        arm_pub.publish(self.command)
    def base_right(self, *args):
        self.command = 'B600'
        arm_pub.publish(self.command)
    def base_stop(self, *args):
        self.command = 'B700'
        arm_pub.publish(self.command)

    def move_shoulder(self, instance, value):
        self.command = 'S' + str(int(value))
        self.shoulder_val.text = str(value)
        arm_pub.publish(self.command)
    def shoulder_set(self, *args):
        self.command = 'S400'
        arm_pub.publish(self.command)
    def shoulder_left(self, *args):
        self.command = 'S500'
        arm_pub.publish(self.command)
    def shoulder_right(self, *args):
        self.command = 'S600'
        arm_pub.publish(self.command)
    def shoulder_stop(self, *args):
        self.command = 'S700'
        arm_pub.publish(self.command)

    def move_elbow(self, instance, value):
        self.command = 'E' + str(int(value))
        self.elbow_val.text = str(value)
        arm_pub.publish(self.command)
    def elbow_set(self, *args):
        self.command = 'E400'
        arm_pub.publish(self.command)
    def elbow_left(self, *args):
        self.command = 'E500'
        arm_pub.publish(self.command)
    def elbow_right(self, *args):
        self.command = 'E600'
        arm_pub.publish(self.command)
    def elbow_stop(self, *args):
        self.command = 'E700'
        arm_pub.publish(self.command)

    def move_pitch(self, instance, value):
        self.command = 'P' + str(int(value))
        self.pitch_val.text = str(value)
        arm_pub.publish(self.command)
    def move_yaw(self, instance, value):
        self.command = 'Y' + str(int(value))
        self.yaw_val.text = str(value)
        arm_pub.publish(self.command)

    def roll_cw(self, *args):
        self.command = 'R1'
        arm_pub.publish(self.command)
    def roll_ccw(self, *args):
        self.command = 'R2'
        arm_pub.publish(self.command)
    def roll_stop(self, *args):
        self.command = 'R0'
        arm_pub.publish(self.command)
    def grip_open(self, *args):
        self.command = 'G1'
        arm_pub.publish(self.command)
    def grip_close(self, *args):
        self.command = 'G2'
        arm_pub.publish(self.command)
    def grip_stop(self, *args):
        self.command = 'G0'
        arm_pub.publish(self.command)   
    def press_a(self, *args):
        self.command = 'X1'
        arm_pub.publish(self.command)
    def press_b(self, *args):
        self.command = 'X2'
        arm_pub.publish(self.command)
    def press_s(self, *args):
        self.command = 'X0'
        arm_pub.publish(self.command)
    def screw_cw(self, *args):
        self.command = 'D1'
        arm_pub.publish(self.command)
    def screw_ccw(self, *args):
        self.command = 'D2'
        arm_pub.publish(self.command)
    def screw_stop(self, *args):
        self.command = 'D0'
        arm_pub.publish(self.command)

    

    def activate_arm_on_value(self, instance, value):
        if int(value) == 1:
            self.command = 'A1'
            self.activate_arm_val.text = "Unlocked"
            arm_pub.publish(self.command)
        if int(value) == 0:
            self.command = 'A0'
            self.activate_arm_val.text = "Locked"
            arm_pub.publish(self.command)

    #arm control functions---------------------------------------------------------------------------------

    #science module functions---------------------------------------------------------------------------------

    
    def pump(self, i,*args):
        self.command = 'P'+str(int(i))
        sci_pub.publish(self.command)
    def pump_stop(self, i,*args):
        self.command = 'Q'+str(int(i))
        sci_pub.publish(self.command)
    def motor(self, i,*args):
        self.command = 'X'+str(int(i))
        sci_pub.publish(self.command)

    #def drill_down(self,*args):
    #    self.command = 'D2'
    #    sci_pub.publish(self.command)
    #def drill_up(self,*args):
    #    self.command = 'D1'
    #    sci_pub.publish(self.command)
    #def drill_stop(self,*args):
    #    self.command = 'D0'
    #    sci_pub.publish(self.command)
    #def drill_cw(self,*args):
    #    self.command = 'S1'
    #    sci_pub.publish(self.command)
    #def drill_ccw(self,*args):
    #    self.command = 'S2'
    #    sci_pub.publish(self.command)
    #def drill_spin_stop(self,*args):
    #    self.command = 'S0'
    #    sci_pub.publish(self.command)
    #def rc_spin(self,*args):
    #    self.command = 'X1'
    #    sci_pub.publish(self.command)
    #def rc_step(self,*args):
    #    self.command = 'X2'
    #    sci_pub.publish(self.command)
    #def rc_stop(self,*args):
    #    self.command = 'X0'
    #    sci_pub.publish(self.command)
    #science module functions---------------------------------------------------------------------------------

    
    
            
    

    #other control functions---------------------------------------------------------------------------------

    def move_slider_on_value(self, instance, value):
        global speed
        speed = int(value)

        self.move_slider_val.text = str(value)

        #self.command = 'S' + str(int(value))
        #move_pub.publish(self.command)

    def cam_feed_slider_on_value(self, instance, value):
        global feed_num 
        feed_num = int(value)
        if(feed_num == 1):
            self.cam_feed_slider_val.text = "Jetson"
        if(feed_num == 2):
            self.cam_feed_slider_val.text = "Arm"
        if(feed_num == 3):
            self.cam_feed_slider_val.text = "Science"
        if(feed_num == 4):
            self.cam_feed_slider_val.text = "Microscope"

    #other control functions---------------------------------------------------------------------------------

    #Timed Functions--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 

    def timed_events(self, *args):

        if(feed_num == 1):
            imageFrame = current_frame_1
            if toggle_1:
                self.cam_text.text = 'Camera Feed (Status:  <<-1  )'
            else:
                self.cam_text.text = 'Camera Feed (Status:  1->>  )'
        if(feed_num == 2):
            imageFrame = current_frame_2
            if toggle_2:
                self.cam_text.text = 'Camera Feed (Status:  <<-2  )'
            else:
                self.cam_text.text = 'Camera Feed (Status:  2->>  )'
        if(feed_num == 3):
            imageFrame = current_frame_3
            if toggle_3:
                self.cam_text.text = 'Camera Feed (Status:  <<-3  )'
            else:
                self.cam_text.text = 'Camera Feed (Status:  3->>  )'
        if(feed_num == 4):
            imageFrame = current_frame_4
            if toggle_4:
                self.cam_text.text = 'Camera Feed (Status:  <<-4  )'
            else:
                self.cam_text.text = 'Camera Feed (Status:  4->>  )'

        buffer = cv2.flip(imageFrame, 0).tostring()
        texture = Texture.create(size=(imageFrame.shape[1], imageFrame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buffer, colorfmt='rgb', bufferfmt='ubyte')
        self.image_feed.texture = texture


        #encoder position updates
        try:
            self.mux_val.text = encoder_pos[0]
        except:
            pass
        try:
            self.base_targ.text = encoder_pos[1]
        except:
            pass
        try:
            self.shoulder_targ.text = encoder_pos[2]
        except:
            pass
        try:
            self.elbow_targ.text = encoder_pos[3]
        except:
            pass
        try:
            self.pitch_targ.text = encoder_pos[4]
        except:
            pass
        try:
            self.yaw_targ.text = encoder_pos[5]
        except:
            pass
	
        #battery status updates
        try:
            self.batt_1_i.text = str(round(int(stat_batt[0])*5.0/1023.0))
        except:
            pass
        try:
            self.batt_1_v.text = stat_batt[1]
        except:
            pass
        try:
            self.batt_2_i.text = str(round((int(stat_batt[2])/1023.0),5)*5)
        except:
            pass
        try:
            self.batt_2_v.text = str(round((int(stat_batt[3])/1023.0),2)*5*2.82)
        except:
            pass
        try:
            self.batt_3_i.text = str(int(stat_batt[4])*5.0/1023.0)
        except:
            pass
        try:
            self.batt_3_v.text = stat_batt[5]
        except:
            pass
        try:
            self.batt_4_i.text = str(int(stat_batt[6])*5.0/1023.0)
        except:
            pass
        try:
            self.batt_4_v.text = stat_batt[7]
        except:
            pass
            
        #Science module updates
        #try:
        #    self.sci_sensor_text_1.text=str(int(sci_str[0])+256)
        #except:
        #    pass
        #try:
        #    self.sci_sensor_text_2.text=str(int(sci_str[1])+463)
        #except:
        #    pass
        #try:
        #    self.sci_sensor_text_3.text=sci_str[2]
        #except:
        #    pass
        
    #Timed Functions--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 

#Camera Feeds and Subscriber Functions----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def callback_img_1(data):
    global current_frame_1
    global toggle_1
    toggle_1 = not toggle_1
    # Used to convert between ROS and OpenCV images
    br = CvBridge()
    # Convert ROS Image message to OpenCV image
    current_frame_1 = br.imgmsg_to_cv2(data)

def callback_img_2(data):
    global current_frame_2
    global toggle_2
    toggle_2  = not toggle_2
    # Used to convert between ROS and OpenCV images
    br = CvBridge()
    # Convert ROS Image message to OpenCV image
    current_frame_2 = br.imgmsg_to_cv2(data)

def callback_img_3(data):
    global current_frame_3
    global toggle_3
    toggle_3  = not toggle_3
    # Used to convert between ROS and OpenCV images
    br = CvBridge()
    # Convert ROS Image message to OpenCV image
    current_frame_3 = br.imgmsg_to_cv2(data)

def callback_img_4(data):
    global current_frame_4
    global toggle_4
    toggle_4  = not toggle_4
    # Used to convert between ROS and OpenCV images
    br = CvBridge()
    # Convert ROS Image message to OpenCV image
    current_frame_4 = br.imgmsg_to_cv2(data)


def callback_move(data): # not required for urc 2022
    #print('move_ok')
    nothing = 1

def callback_arm(data):
    #print('arm ok')
    encoder_str = data.data
    global encoder_pos 
    encoder_pos = encoder_str.split(',',7)

    if encoder_pos[0] == 100:
        encoder_pos[0] = "Connected"
    else:
        encoder_pos[0] = "Not Connected"

    for i in range(1, 6):
        if encoder_pos[i] == "600":
            encoder_pos[i] = "N.A"
        elif encoder_pos[i] == "500":
            encoder_pos[i] = "M.M"
        elif encoder_pos[i] == "450":
            encoder_pos[i] = "N.MUX"

def callback_sci(data): # not required for urc 2022
    #print('sci_ok')
    
    global sci_str
    sci_str=data.data.split(',',3)

def callback_stat(data):
    #print('stat_ok')
    stat_str = data.data
    global stat_batt 
    stat_batt = stat_str.split(',',8)


#Camera Feeds----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    rospy.init_node('gui',anonymous=True)

    vel_pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)

    move_pub = rospy.Publisher('base_to_rvr_move', String, queue_size=10) 
    arm_pub = rospy.Publisher('base_to_rvr_arm', String, queue_size=10) 
    sci_pub = rospy.Publisher('base_to_rvr_sci', String, queue_size=10)
    stat_pub = rospy.Publisher('base_to_rvr_stat', String, queue_size=10)
    

    InterplaneterUIApp().run()

