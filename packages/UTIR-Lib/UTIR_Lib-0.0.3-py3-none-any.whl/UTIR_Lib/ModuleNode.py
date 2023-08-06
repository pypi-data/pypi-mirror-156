from rclpy.node import Node
from std_msgs.msg import String
import os

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

# Publisher, subscriber 노드는 전부 ROS2 documentation에서 가져와서 수정한겁니다.
class PublisherClass(Node):
    
    def __init__(self):
        print("[INFO] publisher initialized")
        
    def pub_setup(self,node_name,topicname,timer_seconds):
        super().__init__(node_name)
        self.publisher_ = self.create_publisher(String, topicname, 10)
        self.topic = topicname
        timer_period = timer_seconds  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def publish(self,input_data):
        self.data = str(input_data)

    def timer_callback(self):
        msg = String()
        msg.data = self.data
        self.publisher_.publish(msg)
        self.get_logger().info("{count} message, contents: {contents}, to {day}.".format(count=self.i, contents = self.data, day=self.topic))
        #self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1


class SubscriberClass(Node):
    
    def __init__(self):
        print("[INFO] publisher initialized")

    def sub_setup(self,subscriberName,TopicName):
        super().__init__(subscriberName)
        self.subscription = self.create_subscription(
            String,
            TopicName,
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info('"%s"' % msg.data)
