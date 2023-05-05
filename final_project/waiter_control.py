#!/usr/bin/env python3
import rospy
from std_msgs.msg import String
from final_project.msg import Order
import time

#, Array_Order

order_array = []

def order_callback(data):
    #rospy.loginfo("the order table is:\t")
    rospy.loginfo(' The order has been placed for table %s and the order type is %s', data.table_number, data.order_type)
    data.placed = True
    order_array.append(data)
    chef_control(data)
    #rospy.loginfo("the order table is:\t %s", data.table_number,"and the order type is:\t %s", data.order_type)
    rospy.loginfo("the array has:\n")
    for order in order_array:
        print("The table number is: ", order.table_number,"\n")
        print("The order type is: ", order.order_type,"\n")
        print("The order is: ", order.placed,"\n")
        print("The order is: ", order.ready,"\n")
        print("The table is: ", order.delivered, "\n")


def waiter_control_node():
    rospy.init_node('waiter_control_node', anonymous=True)
    rospy.Subscriber('order_topic', Order, order_callback)
    rospy.spin()

def chef_control(order):
    # to use the image detection
    # then check the location and if it matches the table in the order, we make delivered = true 
    Chef_Location = 1 #maybe we can have the location as coordinates in another msg file.
    Table_Location = 2
    Home_location = 3
    if order.placed == True:
            #wait for some time for the light to turn green and then move the robot to the chef s location
            move_robot(order, Chef_Location) 
            #use the image detection 
            # then once the light is green,we make the order ready = true
            order.ready =True
            #then we move the robot to the location of the table in the order which should be related  
            move_robot(order, Table_Location) 
            #once it is there we make the order.delivered = True
            order.delivered = True
            #then once it is delivered, we should send it home
            move_robot(order, Home_location)


            



def move_robot(order, location):
    
     #this moves the robot to the location given 
     print("arrived to the location given")
     
     
if __name__ == '__main__':
    waiter_control_node()
    #print("the final array of orders has:")
   



