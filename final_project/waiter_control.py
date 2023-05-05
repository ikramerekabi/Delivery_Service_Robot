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
    #we will move the robot here
    if order.placed == True:
            #time.sleep(5)
            order.ready =True
            move_robot(order)



def move_robot(order):
     #we move the robot to the table in the order 
     #time.sleep(5)
     #go to the table in the order 
     order.delivered = True
     
if __name__ == '__main__':
    waiter_control_node()
    #print("the final array of orders has:")
   



