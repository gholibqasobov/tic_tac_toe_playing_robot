import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from robot_move.figure_to_robot_coord import ROBOT_TARGET_COORDS, ROBOT_Z_COORD, FIGURE_COORDS, HOME_POSE
from pydobot import Dobot
import os
import subprocess



"""
Plan of action
1. subscribe to move_robot topic
2. start the robot
3. if recieved a topic, execute robot_target_move(figure, target_cell)

robot_target_move():
grap the figure based on figure type
move to target cell
go back to home position


should we create a funciton to start the robot?
sounds good idea
"""




def connect_robot(port='/dev/ttyUSB0'):
    """
    Connects to the Dobot robot on the specified port after ensuring appropriate permissions.
    
    Args:
        port (str): Serial port to which the Dobot is connected.
    
    Returns:
        Dobot: Connected Dobot instance.
    
    Raises:
        Exception: If permissions cannot be updated or the robot cannot be connected.
    """
    if not os.access(port, os.R_OK | os.W_OK):
        try:
            print(f"Updating permissions for {port}...")
            subprocess.run(["sudo", "chmod", "666", port], check=True)
            print(f"Permissions updated successfully for {port}.")
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to change permissions for {port}: {e}")
    else:
        print(f"Permissions for {port} are already sufficient.")

    try:
        device = Dobot(port=port)
        print(f"Successfully connected to Dobot on {port}.")
        return device
    except Exception as e:
        raise Exception(f"Failed to connect to Dobot: {e}")


def target_move(device=None, figure='O', cell=None, home_cell=(130, 0, 0),target_height=-10, figure_height=-40, figure_height_offset=20):
    pose = device.get_pose()
    position = pose.position

    x_figure, y_figure = FIGURE_COORDS[figure]

    x_target, y_target = ROBOT_TARGET_COORDS[cell]

    x_home, y_home, z_home = home_cell

    # Picking and Placing Figure to Target
    device.move_to(x_figure, y_figure, figure_height + figure_height_offset, position.r)
    device.move_to(x_figure, y_figure, figure_height, position.r)
    device.suck(True)
    device.move_to(x_figure, y_figure, figure_height + figure_height_offset, position.r)
    device.move_to(x_target, y_target, target_height, position.r)
    device.suck(False)

    device.move_to(x_home, y_home, z_home, position.r)
    


class RobotTargetPositionSubscriber(Node):

    def __init__(self):
        super().__init__('robot_move_subscriber')
        self.get_logger().info("Robot Target Move Position Subscriber Initialized")

        self.robot_device = None
        self.figure_height = -47

        try:
            self.robot_device = connect_robot()
        except Exception as e:
            self.get_logger().error(f"Failed to connect to robot: {e}")

        self.subscription = self.create_subscription(
            String,
            '/robot_move',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%s"' % msg.data)

        try:
            cell = msg.data

            self.get_logger().info(f"Moving robot to place figure")
            target_move(
                self.robot_device, 
                'O', 
                cell, 
                home_cell=HOME_POSE, 
                target_height=-15, 
                figure_height=self.figure_height, 
                figure_height_offset=15)
            
            self.get_logger().info(f"Move complete")
            self.figure_height -= 5
        except Exception as e:
            self.get_logger().error(f"Failed to execute move: {e}")
    
    def destroy_node(self):
        if self.robot_device:
            self.robot_device.close()
            self.get_logger().info("Robot connection closed.")
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)

    robot_subscriber = RobotTargetPositionSubscriber()

    try:
        rclpy.spin(robot_subscriber)
    except KeyboardInterrupt:
        pass
    finally:
        robot_subscriber.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()