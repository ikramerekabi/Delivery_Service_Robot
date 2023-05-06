# Delivery_Service_Robot
Final Project for Software Development for Robotics class

### To build the project

```bash
cd ~/catkin_ws/src/
git clone <this repo url>
cd ../
catkin_make
```

### To run the project

```bash
roscore
roslaunch turtlebot3_gazebo turtlebot3_house.launch
roslaunch turtlebot3_navigation turtlebot3_navigation.launch map_file:=$HOME/map.yaml
rosrun <pkg_name> tablesUI.py
rosrun <pkg_name> autonomousDriving.py
```

