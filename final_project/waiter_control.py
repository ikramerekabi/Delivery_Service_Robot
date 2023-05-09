#!/usr/bin/env python3
import rospy
from std_msgs.msg import String
from final_project.msg import Order
import time
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from tf.transformations import quaternion_from_euler
import actionlib

#, Array_Order
label ="no detections"
global current_order
current_order= Order
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
    global current_order 
    current_order= order
    global label
    global moving 
    global led_flag
    if(current_order.order_type=="Burger"):
        Chef_Location = "chef1"
    elif(current_order.order_type =="Pizza"):
        Chef_Location = "chef2"

    move_to_location(Chef_Location, order.table_number)
    # to use the image detection
    # then check the location and if it matches the table in the order, we make delivered = true 
    #Chef_Location = 1 #maybe we can have the location as coordinates in another msg file.
    #Table_Location = 2
    #Home_location = 3
    # if order.placed == True:
    #         #print("calling the callback")
    #         rospy.Subscriber('labels', String, label_callback)
    #         print("the label we got from the camera is:", label)
    #         if (label =='stop'):
    #              order.ready= True
    #         else:
    #              order.ready = False
    print("came back to the function")
    if(current_order.placed == True):
        print("checked if the order is placed")
        rospy.Subscriber('labels', String, label_callback)
    if(current_order.ready==True):
        rospy.Subscriber('ledsensor', String, ledsensor_callback)
        if(led_flag==1):
            current_order.loaded=True
            move_to_location(order.table_number, order.table_number)
            rospy.Subscriber('ledsensor', String, ledsensor_callback)
            if(led_flag ==1):
                order.delivered=True
                rospy.Subscriber('payment', String, payment_callback)
                order.paid=True
                rospy.Publisher('delivered_signal', String, queue_size=10)
    if order.delivered==True and order.paid ==True:        
            move_to_location('home', 'None')
    print("finished")
   
def payment_callback(data):
    payment_done = True
    
            #wait for some time for the light to turn green and then move the robot to the chef s location
            # move_robot(order, Chef_Location) 
            #use the image detection 
            #then once the light is green,we make the order ready = true
            #order.ready =True
            #then we move the robot to the location of the table in the order which should be related  
            #move_robot(order, Table_Location) 
            #once it is there we make the order.delivered = True
            #order.delivered = True
            #then once it is delivered, we should send it home
            #move_robot(order, Home_location)


def move_to_location(location_name, tableServing):
    global client
    #global robotEvents
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
    #robotEvents.publish(eventMessage)

def label_callback(data):
    print("entered the label callback \n")
    global current_order
    global label
    global moving
    #  #if (data=="red"):
    #  #print("entered the callback")
    #  #print("the data of the label is \t", data.data[:4])
    #  label = data.data[:4]
    #   #& str(label)!= 'caution'):
     
    if data.data == 'green_light':
        label = 'green'
    elif data.data == 'red_light':
        label = 'red'
    else:
        label = 'no detection'

    print("The label we got from the camera is:", label)
    if label == 'red' and moving == True:
        client.cancel_all_goals()
        moving = False
    elif label=='green' and moving == False:
        current_order.ready = True  
        print("the order is ready now \n")
    print("the current_order is ", current_order.ready)
    
    #print("the value of the label from the callback function is:", label)


    #  if(str(label) !='stop' and str(label)!= 'caut'):
    #     print("label is not equal to stop, label is:", label)
    #     label ="no detection"
    #  #if(str(label)!= 'red'):
    #   #  print("label is not equal to red, label is:", label)
    #   #  label ="no detection"
    # #  rospy.loginfo("the array has:\n")
    # #  for order in order_array:
    # #     print("The table number is: ", order.table_number,"\n")
    # #     print("The order type is: ", order.order_type,"\n")
    # #     print("The order is placed: ", order.placed,"\n")
    # #     print("The order is ready: ", order.ready,"\n")
    # #     print("The table is delivered: ", order.delivered, "\n")
       
def ledsensor_callback(data):
    global led_flag
    led_flag= data.data
#def move_robot(order, location):
    
#     #this moves the robot to the location given 
#     print("arrived to the location given")
     
     
if __name__ == '__main__':
    rospy.init_node('waiter_control_node', anonymous=True)
    client = actionlib.SimpleActionClient("move_base", MoveBaseAction)
    rospy.loginfo("Waiting for move_base action server...")
    client.wait_for_server()
    print("finished waiting")
    waiter_control_node()
    
    #print("the final array of orders has:")
    rospy.spin()
   



