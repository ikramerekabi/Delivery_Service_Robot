#!/usr/bin/env python

import rospy
import time
from homework_four.msg import tableMenuSelection
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from tf.transformations import quaternion_from_euler
import actionlib

global client
global robotEvents
# Define the coordinates for the home station, chefs, and tables
locations = {
    #   x: -1.3487775325775146
    #     y: -1.1300030946731567
    #     z: 0.0
    #   orientation: 
    #     x: 0.0
    #     y: 0.0
    #     z: 0.9984077491822599
    #     w: 0.05640892103926045
    # home -10 
    # 'home': {'x': -5.4, 'y': -0.45, 'z': 0.0},
    # 'chef1': {'x': -5.05, 'y': 3.05, 'z': 0.0},
    # 'chef2': {'x': -3.0, 'y': 2.95, 'z': 0.0},
    # 'table1': {'x': 3.2, 'y': -0.75, 'z': 0.0},
    # 'table2': {'x': 4.0, 'y': 4.0, 'z': 0.0},
    # 'table3': {'x': 5.0, 'y': 5.0, 'z': 0.0},
    'home': {'x': (0), 'y': 0, 'z': 0.0},
    'chef1': {'x': (0.7981822490692139), 'y': (1.26476550102233), 'z': 0.0},
    'chef2': {'x': (2.351349353790), 'y': (1.178648471832), 'z': 0.0},
    'table1': {'x':( 2.843219661712), 'y': (-0.27274590730667), 'z': 0.0},
    'table2': {'x':2.74174237251281, 'y':-0.76166058778, 'z': 0.0},
    'table3': {'x': 1.8901512622833, 'y': -0.8873836994171, 'z': 0.0},
}


def customer_selection_callback(msg):
    rospy.loginfo(f"Customer selection received: table {msg.table}, menu {msg.menu}")

    chef_location = 'chef1' if msg.menu == 0 else 'chef2'
    table_location = f'table{msg.table}'

    # Move to the selected chef
    move_to_location(chef_location,msg.table)
    rospy.sleep(10)  # Wait for 10 seconds

    # Move to the selected table
    move_to_location(table_location,msg.table)
    rospy.sleep(10)  # Wait for 10 seconds

    # Move back to the home station
    move_to_location('home',msg.table)


def move_to_location(location_name, tableServing):
    global client
    global robotEvents
    goal = MoveBaseGoal()
    goal.target_pose.header.frame_id = "map"  # Assuming the map frame is "map"
    goal.target_pose.header.stamp = rospy.Time.now()

    location = locations[location_name]
    goal.target_pose.pose.position.x = location['x']
    goal.target_pose.pose.position.y = location['y']
    goal.target_pose.pose.orientation.z = location['z']

    # Convert yaw to a quaternion
    quat = quaternion_from_euler(0, 0,0)
    goal.target_pose.pose.orientation.x = quat[0]
    goal.target_pose.pose.orientation.y = quat[1]
    goal.target_pose.pose.orientation.z = quat[2]
    goal.target_pose.pose.orientation.w = quat[3]


    client.send_goal(goal)
    eventMessage = "Servicing Table "+str(tableServing)+" : Moving to "+location_name
    rospy.loginfo(eventMessage)
    robotEvents.publish(eventMessage)

    # Wait for the robot to reach the location or timeout after 60 seconds
    if client.wait_for_result(rospy.Duration(60)):
        # rospy.loginfo(f"Robot reached {location_name}")
        eventMessage = "Servicing Table "+str(tableServing)+" : Robot reached "+str(location_name)
        rospy.loginfo(eventMessage)
        robotEvents.publish(eventMessage)
    else:
        # rospy.logwarn(f"Failed to reach {location_name} within the timeout")
        eventMessage = "Servicing Table "+str(tableServing)+": Failed to reach "+location_name+"within the specified time "
        rospy.logwarn(eventMessage)
        robotEvents.publish(eventMessage)


if __name__ == "__main__":
    rospy.init_node("turtlebot_navigation")

    robotEvents = rospy.Publisher('/robowaiter/events', String, queue_size=10)  
    client = actionlib.SimpleActionClient("move_base", MoveBaseAction)
    rospy.loginfo("Waiting for move_base action server...")
    client.wait_for_server()

    rospy.Subscriber("/customer/selection", tableMenuSelection, customer_selection_callback)
    rospy.spin()
