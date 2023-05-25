import re
import time

import rospy
from std_msgs.msg import String

COMMAND_RE_PATTERN = re.compile(r"\b[A-Z]\d+\b")

encoder_angles = None
lower_angle = '500'
higher_angle = '600'
stop_code = '700'
# change if anything changes in the hardware or arduino
joint_index_list = ['B', 'S', 'E'] # have to be capital and the same order as the angles in topic
joint_encoder_limit = {
    'B' : [5, 245],
    'S' : [140, 200],
    'E' : [206, 256]
}

ard_pub = rospy.Publisher('/base_to_rvr_arm', String, queue_size=20)

def callback_from_ard(data):
    global encoder_angles
    # rospy.loginfo(f"{data.data}")
    encoder_angles = [int(x) for x in data.data.split(',')[1:-4]]
    # format {'B': 122, 'S': 195, 'E': 261}
    encoder_angles = dict(zip(joint_index_list, encoder_angles))
    # rospy.loginfo(encoder_angles)

def callback_from_commander(data):
    global encoder_angles
    global ard_pub
    if not re.search(COMMAND_RE_PATTERN, data.data):
        # print("Not matched")
        rospy.logerr(f'Received msg does not match pattern, Skipping. data.data:\"{data.data}\"')
        return
    else:
        # print('Matched')
        pass
    
    rospy.loginfo(f"{data.data}")
    joint_code = data.data[0]
    msg = 'Z'

    if encoder_angles is None:
        rospy.logerr(f'Have not received ENCODER ANGLES yet, Skipping.')
        return
    elif encoder_angles[joint_code] \
        not in range(joint_encoder_limit[joint_code][0], joint_encoder_limit[joint_code][1]+1):
        rospy.logerr(f'Out of allowed joint limit for auto control')
        return


    try:
        targ_angle = int(data.data[1:])
        if targ_angle < encoder_angles[joint_code]:
            msg = joint_code + lower_angle
            rospy.loginfo(f"publishing:{msg}, curr:{encoder_angles[joint_code]}, targ:{targ_angle}")
            ard_pub.publish(msg)
            rospy.Rate(10).sleep()
            while targ_angle <= encoder_angles[joint_code]: # joint never stops at exactly the target value
                time.sleep(.08) # wait for 80 millisecond
                rospy.loginfo(f"{joint_code}: curr:{encoder_angles[joint_code]}, targ:{targ_angle}")
                pass
            ard_pub.publish(joint_code + stop_code)
            rospy.Rate(10).sleep()
        elif targ_angle > encoder_angles[joint_code]:
            msg = joint_code + higher_angle
            rospy.loginfo(f"publishing:{msg}, curr:{encoder_angles[joint_code]}, targ:{targ_angle}")
            ard_pub.publish(msg)
            rospy.Rate(10).sleep()
            while targ_angle >= encoder_angles[joint_code]: # joint never stops at exactly the target value
                time.sleep(.08) # wait for 80 millisecond
                rospy.loginfo(f"{joint_code}: curr:{encoder_angles[joint_code]}, targ:{targ_angle}")
                pass
            ard_pub.publish(joint_code + stop_code)
            rospy.Rate(10).sleep()
    except Exception as e:
        rospy.logerr(f"Exception:\"{e}\"")
        pass



def main():
    rospy.init_node('arm_controller', anonymous=True)
    rospy.Subscriber("/rvr_to_base_arm", String, callback=callback_from_ard)
    rospy.Subscriber("/base_to_arm_controller", String, callback=callback_from_commander)
    
    
    while not rospy.is_shutdown():
        rospy.spin() # just wait and listen

if __name__ == '__main__':
    main()
