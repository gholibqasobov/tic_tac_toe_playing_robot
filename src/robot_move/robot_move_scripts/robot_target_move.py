import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from robot_move.figure_to_robot_coord import ROBOT_TARGET_COORDS, ROBOT_Z_COORD, FIGURE_COORDS, HOME_POSE, BOARD_CELL_COORDS
from pydobot import Dobot
import os
import subprocess
from time import sleep


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

FIGURE_CELLS = {'O': [], 'X': []}

# add remaining figures to opponent list
def add_opponent_figure_cells(FIGURE_CELLS=FIGURE_CELLS, computer_figure='O', human_figure='X'):
    for key, value in ROBOT_TARGET_COORDS.items():
        if value not in FIGURE_CELLS[computer_figure]:
            FIGURE_CELLS[human_figure].append(value)


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


def target_move(device=None, figure='O', cell=None, home_cell=(130, 0, 0),target_height=-40, figure_height=-40, figure_height_offset=20):
    pose = device.get_pose()
    position = pose.position

    x_figure, y_figure = FIGURE_COORDS[figure]

    x_target, y_target = ROBOT_TARGET_COORDS[cell]

    x_home, y_home, z_home = home_cell

    # save board coords of corresponding figure (for sorting after game is over)
    FIGURE_CELLS[figure].append((x_target, y_target))
    

    # Picking and Placing Figure to Target
    device.move_to(x_figure, y_figure, figure_height + figure_height_offset, position.r)
    device.move_to(x_figure, y_figure, figure_height, position.r)
    device.suck(True)
    device.move_to(x_figure, y_figure, figure_height + figure_height_offset, position.r)
    device.move_to(x_target, y_target, target_height, position.r)
    device.suck(False)

    device.move_to(x_home, y_home, z_home, position.r)
    

# def sort_figures(figure, figure_cells, figure_height=-50, figure_height_offset=10, device=None, home_cell=(130, 0, 0)):
#     pose = device.get_pose()
#     position = pose.position

#     x_figure_home, y_figure_home = FIGURE_COORDS[figure]
#     x_home, y_home, z_home = home_cell

#     for figure_cell in figure_cells:
#         # Pick and Place Figure to Home position

#         # approach the cell
#         x_figure, y_figure = figure_cell
#         device.move_to(x_figure, y_figure, figure_height + figure_height_offset, position.r)
#         device.move_to(x_figure, y_figure, figure_height, position.r)
#         # grab the figure
#         device.suck(True)
#         device.move_to(x_figure, y_figure, figure_height + figure_height_offset, position.r)
#         device.move_to(x_figure_home, y_figure_home, figure_height + figure_height_offset+10, position.r)
#         device.move_to(x_figure_home, y_figure_home, figure_height, position.r)
#         device.suck(False)
#         # move home
#         device.move_to(x_home, y_home, z_home, position.r)
#         sleep(0.3)

def sort_figures(figure, figure_cells, figure_height=-50, figure_height_offset=10, device=None, home_cell=(130, 0, 0)):
    if device is None or not figure_cells:
        raise ValueError("Device and figure_cells must not be None or empty.")

    if figure not in FIGURE_COORDS:
        raise ValueError("Invalid figure. Ensure it exists in FIGURE_COORDS.")

    pose = device.get_pose()
    position = pose.position

    x_figure_home, y_figure_home = FIGURE_COORDS[figure]
    x_home, y_home, z_home = home_cell

    additional_offset = 10
    i = 0
    for figure_cell in figure_cells:
        x_figure, y_figure = figure_cell

        # Approach the cell
        print("Moving cell", x_figure, y_figure)
        device.move_to(x_figure, y_figure, figure_height + figure_height_offset, position.r)
        device.move_to(x_figure, y_figure, figure_height, position.r)

        # Grab the figure
        device.suck(True)
        device.move_to(x_figure, y_figure, figure_height + figure_height_offset, position.r)

        # Move to the figure home
        device.move_to(x_figure_home, y_figure_home, figure_height + figure_height_offset + additional_offset, position.r)
        device.move_to(x_figure_home, y_figure_home, figure_height + i*5, position.r)

        # Release the figure
        device.suck(False)

        # Move home
        device.move_to(x_home, y_home, z_home, position.r)
        i += 1

        sleep(1)  # Ensure this delay is required for hardware stability


        

        

class RobotTargetPositionSubscriber(Node):

    def __init__(self):
        super().__init__('robot_move_subscriber')
        self.get_logger().info("Robot Target Move Position Subscriber Initialized")

        self.robot_device = None
        self.figure_height = -49
        self.busy = False  # Flag to indicate if the robot is busy

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
        # Check if the robot is already busy
        if self.busy:
            self.get_logger().warn("Robot is busy. Ignoring new command.")
            return

        self.busy = True  # Set the busy flag
        self.get_logger().info('I heard: "%s"' % msg.data)

        try:
            if msg.data == 'game_over':
                self.handle_game_over()
            else:
                self.move_robot_to_target(msg.data)
        except Exception as e:
            self.get_logger().error(f"Error processing command: {e}")
        finally:
            self.busy = False  # Reset the busy flag after processing

    def handle_game_over(self):
        self.get_logger().info("Adding opponent figure cells")
        add_opponent_figure_cells(FIGURE_CELLS, computer_figure='O', human_figure='X')
        sleep(6)

        self.get_logger().info("Collecting O figures")
        sort_figures('O', FIGURE_CELLS['O'], figure_height=-55, figure_height_offset=10, device=self.robot_device, home_cell=(130, 0, 0))
        sleep(15)

        self.get_logger().info("Collecting X figures")
        sort_figures('X', FIGURE_CELLS['X'], figure_height=-55, figure_height_offset=10, device=self.robot_device, home_cell=(130, 0, 0))

    def move_robot_to_target(self, cell):
        self.get_logger().info(f"Moving robot to place figure at cell: {cell}")
        target_move(
            self.robot_device,
            'O',
            cell,
            home_cell=HOME_POSE,
            target_height=-45,
            figure_height=self.figure_height,
            figure_height_offset=25
        )
        self.figure_height -= 5
        self.get_logger().info(f"Move complete. Figure height adjusted to {self.figure_height}")

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