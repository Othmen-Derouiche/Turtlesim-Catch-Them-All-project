# Turtlesim-Catch-Them-All-project

## Project Description:

For this project, I used the Turtlesim package as a simulation tool to visualize the robot's behavior.

### Packages:

- **turtlesim_catch_them_all**: Contains the newly created nodes (a Python package).
- **turtlesim_interfaces**: Includes all interface definitions, including message and service types.
- **turtlesim_bringup**: Holds the launch file for starting the nodes application.

### Nodes Used:

1. `turtlesim_node` from the `turtlesim` package.
2. Custom node named `turtle_controller` to control the turtle named "turtle1" in `turtlesim_node`.
3. Custom node named `turtle_spawner` to spawn turtles and manage which turtle is still “alive”on the window.

## Installation:

Requires a ROS2 distribution (e.g., ROS2 Humble LTS).

1. Clone this repository in your ROS2 workspace.
2. Build the package (`colcon build --symlink-install`).
3. 
## Developpment :

If you want to go further you can, for example:

- Make the new turtles move randomly. You will then need to be able to keep an eye on each turtle,
  and thus dynamically create a subscription for each alive turtle’s pose!
  For that you can create a “middle” node whose goal is to monitor the playground,
  and tell the turtle controller where to go at any given time.

- Change the pen color each time the “master turtle” has caught another turtle.
- Add another “master turtle” node to catch turtles even faster!
## Launching the Simulation:

Launch the simulation with:

```bash
ros2 launch turtlesim turtlesim_catch_them_all.launch.py


