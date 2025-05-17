# # from pydobot import Dobot
# # import os
# # import subprocess

# # def connect_robot(port='/dev/ttyUSB0'):
# #     """
# #     Connects to the Dobot robot on the specified port after ensuring appropriate permissions.
    
# #     Args:
# #         port (str): Serial port to which the Dobot is connected.
    
# #     Returns:
# #         Dobot: Connected Dobot instance.
    
# #     Raises:
# #         Exception: If permissions cannot be updated or the robot cannot be connected.
# #     """
# #     # Check if the user already has permissions
# #     if not os.access(port, os.R_OK | os.W_OK):
# #         try:
# #             print(f"Updating permissions for {port}...")
# #             subprocess.run(["sudo", "chmod", "666", port], check=True)
# #             print(f"Permissions updated successfully for {port}.")
# #         except subprocess.CalledProcessError as e:
# #             raise Exception(f"Failed to change permissions for {port}: {e}")
# #     else:
# #         print(f"Permissions for {port} are already sufficient.")

# #     # Attempt to connect to the robot
# #     try:
# #         device = Dobot(port=port)
# #         print(f"Successfully connected to Dobot on {port}.")
# #         return device
# #     except Exception as e:
# #         raise Exception(f"Failed to connect to Dobot: {e}")
    
# # def target_move(device=None, figure='O', cell=None, height=-10):
# #     pose = device.get_pose()
# #     position = pose.position
# #     device.move_to(192, -4, 0, position.r)

# #     device.close()

# # def main(args=None):
# #     print("Starting the robot")
# #     device = connect_robot()
    
# #     print("Moving to target")
# #     target_move(device=device, height=-10)



from pydobot import Dobot
import os
import subprocess

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

def target_move(device=None, figure='O', height=-10):
    """
    Moves the robot to a target position based on the provided parameters.

    Args:
        device (Dobot): Connected Dobot instance.
        figure (str): Shape or figure to perform (default 'O').
        height (float): Height adjustment for movement (default -10).
    """
    pose = device.get_pose()
    position = pose.position
    # device.move_to(185, 54, position.z, position.r)
    # device.move_to(130, 0, 0, 0)
    # print(f"Current position: {position}")

    # Move to hardcoded target (modify if needed)
    # print("Moving to target position...")
    # device.move_to(192, 64, 0, position.r)
    # print(position)
    device.suck(
        False
    )
    print("Closing connection.")
    device.close()

def main(args=None):
    device = None
    try:
        print("Starting the robot")
        device = connect_robot()
        print("Moving to target")
        target_move(device=device, height=-10)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if device:
            device.close()
            print("Robot connection closed.")

if __name__ == "__main__":
    main()

# from robot_move.figure_to_robot_coord import ROBOT_TARGET_COORDS

# print(ROBOT_TARGET_COORDS)