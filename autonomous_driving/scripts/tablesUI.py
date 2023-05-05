import sys
import rospy
from std_msgs.msg import String
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                             QHBoxLayout, QWidget, QComboBox, QLabel)
from homework_four.msg import tableMenuSelection

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        rospy.init_node('customer_selection_publisher')  # Initialize the rospy node
        self.publisher = rospy.Publisher('/customer/selection', tableMenuSelection, queue_size=10)  # Create a publisher for the "/customer/selection" topic
        self.event_subscriber = rospy.Subscriber('/robowaiter/events', String, self.event_callback)

        self.setWindowTitle("SDR Robo restaurent")
        self.setMinimumSize(QSize(600, 400))  # Set a minimum size for the main window

        # Create the central widget and set the layout
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Create a QLabel to display the event messages
        self.event_label = QLabel()
        layout.addWidget(self.event_label)

        # Create a horizontal layout for the table buttons
        button_layout = QHBoxLayout()

        # Create table buttons and drop-down menus
        self.table1_button = QPushButton("Table 1")
        self.table1_dropdown = QComboBox()
        self.table1_dropdown.addItem("Select Menu List for Table 1")
        self.table1_dropdown.addItem("Chef 1 special menu")
        self.table1_dropdown.addItem("Chef 2 special menu")
        self.table1_dropdown.setVisible(False)

        self.table2_button = QPushButton("Table 2")
        self.table2_dropdown = QComboBox()
        self.table2_dropdown.addItem("Select Menu List for Table 2")
        self.table2_dropdown.addItem("Chef 1 special menu")
        self.table2_dropdown.addItem("Chef 2 special menu")
        self.table2_dropdown.setVisible(False)

        self.table3_button = QPushButton("Table 3")
        self.table3_dropdown = QComboBox()
        self.table3_dropdown.addItem("Select Menu List for Table 3")
        self.table3_dropdown.addItem("Chef 1 special menu")
        self.table3_dropdown.addItem("Chef 2 special menu")
        self.table3_dropdown.setVisible(False)

        # Connect signals to custom methods
        self.table1_button.clicked.connect(self.show_dropdown1)
        self.table1_dropdown.currentIndexChanged.connect(self.select_menu1)

        self.table2_button.clicked.connect(self.show_dropdown2)
        self.table2_dropdown.currentIndexChanged.connect(self.select_menu2)

        self.table3_button.clicked.connect(self.show_dropdown3)
        self.table3_dropdown.currentIndexChanged.connect(self.select_menu3)

        # Add elements to the button layout
        button_layout.addWidget(self.table1_button)
        button_layout.addWidget(self.table2_button)
        button_layout.addWidget(self.table3_button)

        # Add elements to the main layout
        layout.addLayout(button_layout)
        layout.addWidget(self.table1_dropdown)
        layout.addWidget(self.table2_dropdown)
        layout.addWidget(self.table3_dropdown)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    # Callback function for the "/robowaiter/events" subscriber
    def event_callback(self, msg):
        self.event_label.setText(msg.data)

    def show_dropdown1(self):
        self.table1_dropdown.setVisible(True)

    def show_dropdown2(self):
        self.table2_dropdown.setVisible(True)

    def show_dropdown3(self):
        self.table3_dropdown.setVisible(True)

    def select_menu1(self, index):
        if index != 0:
            self.table1_button.setText(f"Table 1 - Ordered ({self.table1_dropdown.currentText()})")
            self.table1_dropdown.setCurrentIndex(0)
            self.table1_dropdown.setVisible(False)
            self.publisher.publish(1, index - 1) 

    def select_menu2(self, index):
        if index != 0:
            self.table2_button.setText(f"Table 2 - Ordered ({self.table2_dropdown.currentText()})")
            self.table2_dropdown.setCurrentIndex(0)
            self.table2_dropdown.setVisible(False)
            self.publisher.publish(2, index - 1) 

    def select_menu3(self, index):
        if index != 0:
            self.table3_button.setText(f"Table 3 - Ordered ({self.table3_dropdown.currentText()})")
            self.table3_dropdown.setCurrentIndex(0)
            self.table3_dropdown.setVisible(False)
            self.publisher.publish(3, index - 1) 

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()