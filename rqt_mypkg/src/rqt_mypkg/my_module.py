#!/usr/bin/env python3
import os
import rospy
import rospkg
from std_msgs.msg import String
from qt_gui.plugin import Plugin
from python_qt_binding import loadUi
from python_qt_binding.QtWidgets import QWidget
from final_project.msg import Order
#, Array_Order
#order_array = Array_Order()
new_order = Order()
class MyPlugin(Plugin):

    def __init__(self, context):
        super(MyPlugin, self).__init__(context)
        # Give QObjects reasonable names
        self.setObjectName('MyPlugin')

        # Process standalone plugin command-line arguments
        from argparse import ArgumentParser
        parser = ArgumentParser()
        # Add argument(s) to the parser.
        parser.add_argument("-q", "--quiet", action="store_true",
                      dest="quiet",
                      help="Put plugin in silent mode")
        args, unknowns = parser.parse_known_args(context.argv())
        if not args.quiet:
            print ('arguments: ', args)
            print ('unknowns: ', unknowns)

        # Create QWidget
        self._widget = QWidget()
        # Get path to UI file which should be in the "resource" folder of this package
        ui_file = os.path.join(rospkg.RosPack().get_path('rqt_mypkg'), 'resource', 'MyPlugin.ui')
        # Extend the widget with all attributes and children from UI file
        loadUi(ui_file, self._widget)
        # Give QObjects reasonable names
        self._widget.setObjectName('MyPluginUi')
        # Show _widget.windowTitle on left-top of each plugin (when 
        # it's set in _widget). This is useful when you open multiple 
        # plugins at once. Also if you open multiple instances of your 
        # plugin at once, these lines add number to make it easy to 
        # tell from pane to pane.
        if context.serial_number() > 1:
            self._widget.setWindowTitle(self._widget.windowTitle() + (' (%d)' % context.serial_number()))
        # Add widget to the user interface
        context.add_widget(self._widget)
        self._widget.Burger_button.clicked.connect(self.burger_order) 
        self._widget.Pizza_button.clicked.connect(self.pizza_order) 
        #self._widget.Stop_Button.clicked.connect(self.function2) 
        #self._widget.Order_button.clicked.connect(self.open_new_window)
        #self._widget.Table1_button.clicked.connect(self.waiting_function)



    #def open_new_window(self):
        


    def waiting_function(self):
        self.new_window = loadUi(os.path.join(rospkg.RosPack().get_path('rqt_mypkg'), 'resource', 'waiting.ui'))
        self.new_window.show()


    def burger_order(self):
        global new_order
        #new_order = Order()
        self.new_window = loadUi(os.path.join(rospkg.RosPack().get_path('rqt_mypkg'), 'resource', 'Tables.ui'))
        self.new_window.show()
        self.new_window.Table1_button.clicked.connect(lambda: setattr(new_order, "table_number", 1))
        self.new_window.Table2_button.clicked.connect(lambda: setattr(new_order, "table_number", 2))
        self.new_window.Table3_button.clicked.connect(lambda: setattr(new_order, "table_number", 3))
        new_order.order_type = "Burger"
        new_order.placed= "False"
        new_order.ready="False"
        new_order.delivered="False"

        def publish_order():
            pub = rospy.Publisher('order_topic', Order, queue_size=10)
            pub.publish(new_order)
            print('A burger order is placed')
            self.new_window.close()

        self.new_window.Table1_button.clicked.connect(publish_order)
        self.new_window.Table2_button.clicked.connect(publish_order)
        self.new_window.Table3_button.clicked.connect(publish_order)
        rospy.Subscriber('delivered_signal', String, delivered_signal_callback )
        #new_order.table_number=2
        #new_order.table_number=3
        #pub = rospy.Publisher('order_topic', Order, queue_size=10)
        #pub.publish(new_order)
        #print('A burger order is placed')
        
        
        


            
    def delivered_signal_callback(self):
        self.new_window = loadUi(os.path.join(rospkg.RosPack().get_path('rqt_mypkg'), 'resource', 'delivered.ui'))
        self.new_window.show()
    def pizza_order(self):
        global new_order
        #new_order = Order()
        self.new_window = loadUi(os.path.join(rospkg.RosPack().get_path('rqt_mypkg'), 'resource', 'Tables.ui'))
        self.new_window.show()
        self.new_window.Table1_button.clicked.connect(lambda: setattr(new_order, "table_number", "table1"))
        self.new_window.Table2_button.clicked.connect(lambda: setattr(new_order, "table_number", "table2"))
        self.new_window.Table3_button.clicked.connect(lambda: setattr(new_order, "table_number", "table3"))
        new_order.order_type = "Pizza"
        new_order.placed= "False"
        new_order.ready="False"
        new_order.delivered="False"

        def publish_order():
            pub = rospy.Publisher('order_topic', Order, queue_size=10)
            pub.publish(new_order)
            print('A pizza order is placed')
            self.new_window.close()

        self.new_window.Table1_button.clicked.connect(publish_order)
        self.new_window.Table2_button.clicked.connect(publish_order)
        self.new_window.Table3_button.clicked.connect(publish_order)
        rospy.Subscriber('delivered_signal', String,delivered_signal_callback )
        
   

    def shutdown_plugin(self):
        # TODO unregister all publishers here
        pass

    def save_settings(self, plugin_settings, instance_settings):
        # TODO save intrinsic configuration, usually using:
        # instance_settings.set_value(k, v)
        pass

    def restore_settings(self, plugin_settings, instance_settings):
        # TODO restore intrinsic configuration, usually using:
        # v = instance_settings.value(k)
        pass

    #def trigger_configuration(self):
        # Comment in to signal that the plugin has a way to configure
        # This will enable a setting button (gear icon) in each dock widget title bar
        # Usually used to open a modal configuration dialog