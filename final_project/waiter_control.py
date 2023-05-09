#!/usr/bin/env python3
import rospy
from std_msgs.msg import String
from final_project.msg import Order
import time
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from tf.transformations import quaternion_from_euler
import actionlib
from threading import Thread
from nav_msgs.msg import Odometry
import math



#, Array_Order
label ="no detections"
global current_order
current_order= Order
order_exists = False
current_destination = "home"
current_tableServing = 0
current_destination_entity = "home"
made_it_to_goal = False
robot_Stopped = True
order_array = []
global client
global led_flag
global moving 
global last_goal
global last_goal_name
global payment_done
moving = False
last_goal = None
payment_done = False
# Define the coordinates for the home station, chefs, and tables
locations = {
    'home': {'x': (0), 'y': 0, 'z': 0.0},
    'chef1': {'x': (0.7981822490692139), 'y': (1.26476550102233), 'z': 0.0},
    'chef2': {'x': (2.351349353790), 'y': (1.178648471832), 'z': 0.0},
    'table1': {'x':( 2.843219661712), 'y': (-0.27274590730667), 'z': 0.0},
    'table2': {'x':2.74174237251281, 'y':-0.76166058778, 'z': 0.0},
    'table3': {'x': 1.8901512622833, 'y': -0.8873836994171, 'z': 0.0},
}

def order_callback(data):
    global current_order
    current_order = data
    #rospy.loginfo("the order table is:\t")
    rospy.loginfo(' The order has been placed for table %s and the order type is %s', data.table_number, data.order_type)
    data.placed = True
    order_array.append(data)
    chef_control(current_order)
    #rospy.loginfo("the order table is:\t %s", data.table_number,"and the order type is:\t %s", data.order_type)
    rospy.loginfo("the array has:\n")
    for order in order_array:
        print("The table number is: ", order.table_number,"\n")
        print("The order type is: ", order.order_type,"\n")
        print("The order is placed: ", order.placed,"\n")
        print("The order is ready: ", order.ready,"\n")
        print("The table is delivered: ", order.delivered, "\n")

def waiter_control_node():
    rospy.Subscriber('order_topic', Order, order_callback)


def chef_control(order):
    print("entered the chef control \n")
    global current_order, order_exists, label, moving, led_flag, current_destination, current_tableServing, current_destination_entity
    current_order= order
    order_exists = True 

    if(current_order.order_type=="Burger"):
        Chef_Location = "chef1"
    elif(current_order.order_type =="Pizza"):
        Chef_Location = "chef2"

    current_destination = Chef_Location
    current_tableServing = order.table_number
    current_destination_entity = "chef"
    move_to_location(Chef_Location, order.table_number)
    # to use the image detection
    # then check the location and if it matches the table in the order, we make delivered = true 
    #Chef_Location = 1 #maybe we can have the location as coordinates in another msg file.
    #Table_Location = 2
    #Home_location = 3 
    robot_Stopped = False

    print("came back to the function")
    t1 = Thread(target=LoaderInitialize)
    t1.start() 

    t2 = Thread(target=PaymentInitialize)
    t2.start() 
    
    t3 = Thread(target=ReadLabels)
    t3.start()      

    t4 = Thread(target=CheckPosition)
    t4.start()      
    rospy.sleep(0.1)
    rospy.spin()

def LoaderInitialize():
    rospy.Subscriber('ledsensor', String, ledsensor_callback)

def PaymentInitialize():
    rospy.Subscriber('payment', String, payment_callback)

def ReadLabels():
    rospy.Subscriber('labels', String, label_callback)

def PositionSubscription():
    rospy.Subscriber("/odom", Odometry, position_callback)

def position_callback(msg):
    global last_goal, made_it_to_goal
    made_it_to_goal = CheckPosition(last_goal, msg.pose.pose)
    if made_it_to_goal:         
        print("Made it to the Goal \n")

 
def CheckPosition(pose1, pose2): 
    if math.sqrt((pose1.x - pose2.x)**2+(pose1.y - pose2.y)**2) < .5:
        return True

    return False
   
def payment_callback(data):
    payment_done = True
    
    if data.data == "1":
        move_to_location("home",0)


def move_to_location(location_name, tableServing):
    global client, last_goal
    #global robotEvents
    global moving
    global last_goal
    global last_goal_name
    made_it_to_goal = False

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
    #robotEvents.publish(eventMessage)

def label_callback(data):
    print("entered the label callback \n")
    global current_order, order_exists, label, moving, current_order, current_tableServing, current_destination, made_it_to_goal, current_destination_entity
 
    if data.data == 'green_light':
        label = 'green'
        move_to_location(current_destination, current_tableServing)
    elif data.data == 'red_light':
        label = 'red'
        StopMoving() 
    elif moving == False and data.data == 'B':
        made_it_to_goal = True
        print("Made it to the Goal \n")

    else:
        label = 'no detection'

    print("The label we got from the camera is:", label)

    #If Stopped and See Green Label - Continue to destination
    #If At Chef's location and get green label - order is ready go to table   
    determine_Next_Destination()  
         
def StopMoving():
    global robot_Stopped, moving
    robot_Stopped = True
    moving = False

    client.cancel_all_goals()

def determine_Next_Destination():
  global current_order, label, moving, current_order, current_tableServing, current_destination, made_it_to_goal, current_destination_entity

  if made_it_to_goal and current_destination_entity == "chef":
        current_destination = "table1"
        current_tableServing = current_order.table_number
        current_destination_entity = "table"
        current_order.ready = True  

        print("the order is ready now \n")
        print("the current_order is ", current_order.ready)
        move_to_location(current_destination, current_tableServing)
  elif made_it_to_goal and current_destination_entity == "table":
        move_to_location("home", 0)

        print("the order is delivered\n")
  else:
        move_to_location(current_destination, current_tableServing)
        print("Continuing to destination\n")    

def ledsensor_callback(data):
    global led_flag
    global current_order, label, moving, current_order, current_tableServing, current_destination, made_it_to_goal, current_destination_entity

    led_flag= data.data
    if moving == False:        
        determine_Next_Destination()
    else:
        StopMoving()         
     
     
if __name__ == '__main__':
    rospy.init_node('waiter_control_node', anonymous=True)
    client = actionlib.SimpleActionClient("move_base", MoveBaseAction)
    rospy.loginfo("Waiting for move_base action server...")
    client.wait_for_server()
    print("finished waiting")
    waiter_control_node()
    
    #print("the final array of orders has:")
    rospy.spin()
   



