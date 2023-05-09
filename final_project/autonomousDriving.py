#!/usr/bin/env python3

import rospy
import time
from std_msgs.msg import String
from final_project.msg import tableMenuSelection
from geometry_msgs.msg import PoseStamped
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from tf.transformations import quaternion_from_euler
import actionlib

global client
global robotEvents

global current_selected_chef
global current_selected_table
global next_selections


current_selected_chef = None
current_selected_table = None
next_selections = []

global moving
global loaded
global payment_received
global last_goal
global last_goal_name

moving = False
loaded = False
payment_received = False
last_goal = None

# Define the coordinates for the home station, chefs, and tables
locations = {
    'home': {'x': (0), 'y': 0, 'z': 0.0},
    'chef1': {'x': (0.7981822490692139), 'y': (1.26476550102233), 'z': 0.0},
    'chef2': {'x': (2.351349353790), 'y': (1.178648471832), 'z': 0.0},
    'table1': {'x':( 2.843219661712), 'y': (-0.27274590730667), 'z': 0.0},
    'table2': {'x':2.74174237251281, 'y':-0.76166058778, 'z': 0.0},
    'table3': {'x': 1.8901512622833, 'y': -0.8873836994171, 'z': 0.0},
}

def sendRobotEvents(event):
    global robotEvents
    rospy.loginfo(event)
    robotEvents.publish(event)

###
###  Customer selectionn capture starts here
###

def customer_selection_callback(msg):
    global next_selections

    rospy.loginfo(f"Customer selection received: table {msg.table}, menu {msg.menu}")

    chef_location = 'chef1' if msg.menu == 0 else 'chef2'
    table_location = f'table{msg.table}'

    next_selections.append((chef_location, table_location))
    process_next_selection()


def process_next_selection():
    global current_selected_chef
    global current_selected_table
    global next_selections

    if not next_selections:
        rospy.logwarn("No selections to process")
        return

    current_selected_chef, current_selected_table = next_selections.pop(0)

    # Move to the selected chef
    move_to_location(current_selected_chef, current_selected_table)


def move_to_location(location_name, tableServing):
    global client
    global robotEvents
    global moving
    global last_goal
    global last_goal_name

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
    moving = True
    last_goal = goal
    last_goal_name=location_name
    

    eventMessage = "Servicing "+str(tableServing)+" : Moving to "+location_name
    rospy.loginfo(eventMessage)
    robotEvents.publish(eventMessage)
    wait_for_client_goal()


def wait_for_client_goal():
    global client
    global last_goal_name
    global current_selected_table

    # Wait for the robot to reach the location or timeout after 60 seconds
    if client.wait_for_result(rospy.Duration(60)):
        # rospy.loginfo(f"Robot reached {location_name}")
        eventMessage = "Servicing "+str(current_selected_table)+" : Robot reached "+str(last_goal_name)
        rospy.loginfo(eventMessage)
        robotEvents.publish(eventMessage)
    else:
        # rospy.logwarn(f"Failed to reach {location_name} within the timeout")
        eventMessage = "Servicing "+str(current_selected_table)+": Failed to reach "+last_goal_name+" within the specified time "
        rospy.logwarn(eventMessage)
        #robotEvents.publish(eventMessage)
    if last_goal_name =="home":
        process_next_selection()


# checks for the object detection status
def yolov5_callback(msg):
    global moving
    global last_goal

    if msg.labels == "stop" and moving == True :

        rospy.loginfo("Received stop event")
        client.cancel_all_goals()
        moving = False

        sendRobotEvents("Servicing "+str(current_selected_table)+" : Stopped for a stop signal")

    elif msg.labels == "green" and moving == False:

        rospy.loginfo("Received green event")
        if last_goal is not None:
            client.send_goal(last_goal)
            moving = True
            
            sendRobotEvents("Servicing "+str(current_selected_table)+" : Started towards "+last_goal_name+" on green signal")
            wait_for_client_goal()

        else:
            rospy.logwarn("No previous goal to resume")


## checks for the loading event status

def load_callback(msg):
    global loaded
    global current_selected_chef
    global current_selected_table

    if msg.data == "loaded":
        rospy.loginfo("Loaded event received")
        loaded = True
        if current_selected_table is not None:
            # Move to the selected table
            move_to_location(current_selected_table, current_selected_table)
        else:
            rospy.logwarn("No table location available")
    elif msg.data == "unloaded":
        loaded = False
        complete_the_order()


## Checks for the payment status
def payment_callback(msg):
    global payment_received
    if msg.data == "paid":
        payment_received = True
        complete_the_order()



def complete_the_order():
    global loaded
    global payment_received

    if loaded == False and payment_callback == True:
        move_to_location("home", current_selected_table)


if __name__ == "__main__":
    rospy.init_node("turtlebot_navigation")

    robotEvents = rospy.Publisher('/robowaiter/events', String, queue_size=10)  
    client = actionlib.SimpleActionClient("move_base", MoveBaseAction)
    rospy.loginfo("Waiting for move_base action server...")
    client.wait_for_server()
    rospy.Subscriber("/customer/selection", tableMenuSelection, customer_selection_callback)
    rospy.Subscriber("/yolov5/events", String, yolov5_callback)
    rospy.Subscriber("/load/events", String, load_callback)
    rospy.Subscriber("/payment/events", String, payment_callback)
    rospy.spin()
