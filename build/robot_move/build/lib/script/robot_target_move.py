import rclpy
from rclpy.node import Node
# Import a specific function/class from your module
from robot_move.module_to_import import function_to_import
class MyPythonNode(Node):
    def __init__(self):
        super().__init__("my_node_name")
# Run the imported function
        function_to_import()
def main(args=None):
    # Initiate ROS communications
    rclpy.init(args=args)
    # Instantiate the node
    node = MyPythonNode()
    # Make the node spin
    rclpy.spin(node)
    # Destroy the node object
    node.destroy_node()
    # Shutdown ROS communications
    rclpy.shutdown()

if __name__ == '__main__':
    main()
