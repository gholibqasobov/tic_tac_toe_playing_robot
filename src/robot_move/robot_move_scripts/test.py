class RobotTargetPositionSubscriber(Node):

    def __init__(self):
        super().__init__('robot_move_subscriber')
        self.get_logger().info("Robot Target Move Position Subscriber Initialized")

        self.robot_device = None
        self.figure_height = -47
        self.busy = False  # Flag to indicate if the robot is busya

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
        add_opponent_figure_cells(FIGURE_CELLS, computer_figure='X', human_figure='O')
        sleep(4)

        self.get_logger().info("Collecting X figures")
        sort_figures('X', FIGURE_CELLS['X'], figure_height=-53, figure_height_offset=10, device=self.robot_device, home_cell=(130, 0, 0))
        sleep(5)

        self.get_logger().info("Collecting O figures")
        sort_figures('O', FIGURE_CELLS['O'], figure_height=-53, figure_height_offset=10, device=self.robot_device, home_cell=(130, 0, 0))

    def move_robot_to_target(self, cell):
        self.get_logger().info(f"Moving robot to place figure at cell: {cell}")
        target_move(
            self.robot_device,
            'X',
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
