#!/usr/bin/env python3
import rclpy
import random
import math
from rclpy.node import Node
from turtlesim.srv import Spawn , Kill # service type
from turtlesim_interfaces.msg import TurtleArray , Turtle
from turtlesim_interfaces.srv import CatchTurtle
from functools import partial

class TurtleSpawnerNode(Node): 
    def __init__(self):

        super().__init__("turtle_spawner") 

        self.declare_parameter("spawnfrequency",1.0)
        self.declare_parameter("turtle_name_prefix","Otty_turtle_")
        #self.declare_parameter("self.use_sim_time","10.0")

        self.spawnfrequency = self.get_parameter("spawnfrequency").value
        self.turtle_name_prefix = self.get_parameter("turtle_name_prefix").value
        #self.use_sim_time = self.get_parameter("use_sim_time").value

        """------------------------------------------------------------------"""

        self.turtle_counter = 0
        self.alive_turtles = []
        
        """------------------------------------------------------------------"""
        self.alive_turtle_publisher = self.create_publisher(TurtleArray ,'alive_turtles',10)
        self.get_logger().info("alive turtle publisher has been started ")

        # spawn a turtle at a given rate 
        self.spawn_turtle_timer = self.create_timer( 1.0/self.spawnfrequency , self.spawn_new_turtle)

        # call kill service and remove the turtle from the array of alive turtles.
        self.catch_turtle_service = self.create_service(CatchTurtle,'catch_turtle',self.callback_catch_turtle)
        self.get_logger().info("catch turtleserver has been started ")
        

    """------------------------------------------------------------------"""
    def call_kill_server(self,turtle_name):

        killClient = self.create_client(Kill,'/kill') # service definition / service name
        while not killClient.wait_for_service(1.0): # after 1.0 s the wait_for_service will exit and we keep staying in while
            self.get_logger().warn("waiting for the server  .....")
        
        request = Kill.Request()
        request.name = turtle_name
        
        future = killClient.call_async(request)
        future.add_done_callback(partial(self.callback_call_kill,turtle_name = turtle_name)) # we will add a callback function when the future is complete cad the server has sent a response

    """------------------------------------------------------------------"""
    def callback_call_kill(self,future,turtle_name):
        try:
            response = future.result()
            # remove the turtle from alive_turtle list 
            for (i , turtle) in enumerate(self.alive_turtles):
                if (turtle.name == turtle_name):
                    del self.alive_turtles[i]
                    self.publish_alive_turtles() # Important
                    self.get_logger().info("The caught turtle has been removed")
                    break
        except Exception as e:
            self.get_logger().error(" service call failed  %r " %(e,))
    
    """------------------------------------------------------------------"""
    def callback_catch_turtle(self,request,response):

        self.call_kill_server(request.name)
        response.success = True
        
        return response

    """------------------------------------------------------------------"""
    """------------------------------------------------------------------"""

    def publish_alive_turtles(self):

        msg = TurtleArray()
        msg.turtles = self.alive_turtles

        self.alive_turtle_publisher.publish(msg)
    
    """------------------------------------------------------------------"""
    def call_spawn_server(self,turtle_name,x,y,theta):

        spawnClient = self.create_client(Spawn,"/spawn") # service definition / service name
        # create a new turtle (choose random coordinates between 
        # 0.0 and 11.0 for both x and y)
        
        while not spawnClient.wait_for_service(1.0): # after 1.0 s the wait_for_service will exit and we keep staying in while
            self.get_logger().warn("waiting for the server  .....")
        
        request = Spawn.Request()
        request.x = x
        request.y = y
        request.theta = theta
        request.name = turtle_name

        future = spawnClient.call_async(request)
        future.add_done_callback(partial(
            self.callback_call_spawn,turtle_name=turtle_name,x=x,y=y,theta=theta)) # we will add a callback function when the future is complete cad the server has sent a response
    
    """------------------------------------------------------------------"""
    def callback_call_spawn(self,future,turtle_name,x,y,theta):
        try:
            response = future.result()
            if response.name != "": # if empty -> the turtle is not spawned
                self.get_logger().info("Turtle" + response.name + " is now alive")

                new_turtle = Turtle()
                new_turtle.name = response.name
                new_turtle.x = x
                new_turtle.y = y
                new_turtle.theta = theta
                self.alive_turtles.append(new_turtle)
                self.publish_alive_turtles()

        except Exception as e:
            self.get_logger().error(" service call failed  %r " %(e,))

    """------------------------------------------------------------------"""
    def spawn_new_turtle(self):

        self.turtle_counter += 1
        name = self.turtle_name_prefix + str(self.turtle_counter)
        x = random.uniform(1.0 , 10.0)
        y = random.uniform(1.0 , 10.0)
        theta = random.uniform(0.0 , 2*math.pi)

        self.call_spawn_server(name,x,y,theta)

def main(args=None):
    rclpy.init(args=args)
    node = TurtleSpawnerNode() 
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()