#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from turtlesim_interfaces.msg import TurtleArray , Turtle
from turtlesim_interfaces.srv import CatchTurtle
from functools import partial
import math

# control the master turtle 
class TurtleControllerNode(Node): 
    def __init__(self):
        super().__init__("turtle_controller_node")

        self.declare_parameter("catch_closest_turtle_first",True)
        # self.declare_parameter("use_sim_time","10.0")

        self.catch_closest_turtle_first = self.get_parameter("catch_closest_turtle_first").value
        #self.use_sim_time = self.get_parameter("use_sim_time").value
        
        """-------------------------------------------------------------"""

        self.pose = None
        self.turtle_to_catch = None
        
        """-------------------------------------------------------------"""

        self.pose_subscriber = self.create_subscription(Pose,
                                "turtle1/pose",self.callback_turtle_pose,10)
        
        self.get_logger().info("pose subscriber has been started")
        
        self.cmd_vel_publisher = self.create_publisher(Twist, 
                                "turtle1/cmd_vel",10)
        
        self.get_logger().info("cmd_vel publisher has been started")

        self.control_timer = self.create_timer(0.01,self.control_loop) # freq = 100 Hz

        self.alive_turtles_subscriber = self.create_subscription(TurtleArray ,
                                'alive_turtles',self.callback_alive_turtles,10)
        
        self.get_logger().info("alive turtles subscriber has been started")
    
    """------------------------------------------------------------------"""
    def call_catch_turtle_server(self,turtle_name):

        catchTurtleClient = self.create_client(CatchTurtle,'catch_turtle') # service definition / service name
        while not catchTurtleClient.wait_for_service(1.0): # after 1.0 s the wait_for_service will exit and we keep staying in while
            self.get_logger().warn("waiting for the server  .....")
        
        request = CatchTurtle.Request()
        request.name = turtle_name
        
        future = catchTurtleClient.call_async(request)
        future.add_done_callback(partial(self.callback_call_catch_turtle,turtle_name = turtle_name)) 
        # we will add a callback function when the future is complete cad the server has sent a response

    """------------------------------------------------------------------"""
    def callback_call_catch_turtle(self,future,turtle_name):
        try:
            response = future.result()
            if not response.success :
                self.get_logger().info("Turtle " + str(turtle_name) + "could not be caught")
        except Exception as e:
            self.get_logger().error(" service call failed  %r " %(e,))
    """-------------------------------------------------------------"""
    def callback_alive_turtles(self,msg):
        if len(msg.turtles) > 0 :
            if self.catch_closest_turtle_first :
                #  catch the closest turtle
                closest_turtle = None
                closest_turtle_distance = None

                for turtle in msg.turtles:
                    dist_x = turtle.x - self.pose.x
                    dist_y = turtle.y = self.pose.y
                    distance = math.sqrt((dist_x)**2 + (dist_y)**2)
                    if closest_turtle == None or distance > closest_turtle_distance :
                        closest_turtle = turtle 
                        closest_turtle_distance = distance
                self.turtle_to_catch = closest_turtle
            
            else : 
                #  catch the first turtle
                self.turtle_to_catch = msg.turtles[0] 
            
        
    """-------------------------------------------------------------"""
    
    def callback_turtle_pose(self,msg):

        self.pose = msg
        # the pose will be automatically updated whenever a new message arrives

    """-------------------------------------------------------------"""

    # check the target position , the master position , 
    # what we need to do to reach the target , send command velocity
    def control_loop(self):
        if self.pose == None or self.turtle_to_catch == None:
            return
        
        dist_x = self.turtle_to_catch.x - self.pose.x
        dist_y = self.turtle_to_catch.y - self.pose.y

        distance = math.sqrt((dist_x)**2 + (dist_y)**2)
        
        msg = Twist()

        if distance > 0.5:

            ## Position
            K_p_linear = 2 # to be tuned
            msg.linear.x = K_p_linear * distance 
            # distance is an error which is given as a command (P controller)
            
            ## Orientation
            goal_theta = math.atan2(dist_y , dist_x)
            diff = goal_theta - self.pose.theta 

            # normalize the angle between -pi and pi
            if diff > math.pi :
                diff -= 2 * math.pi
            elif diff < -math.pi :
                diff += 2 * math.pi

            K_p_angular = 6 # to be tuned
            msg.angular.z = K_p_angular * diff


        else : 
            # stop the turtle when the target is reached 

            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.call_catch_turtle_server(self.turtle_to_catch.name)
            self.turtle_to_catch = None 
            # when we reached the target , 
            # it is useless to continue running the control loop

        self.cmd_vel_publisher.publish(msg)

    """-------------------------------------------------------------"""


def main(args=None):
    rclpy.init(args=args)
    node = TurtleControllerNode() 
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()