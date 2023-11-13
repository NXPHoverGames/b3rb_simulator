from os import environ
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.actions import ExecuteProcess
from launch.conditions import LaunchConfigurationEquals, IfCondition
from launch_ros.actions import Node


ARGUMENTS = [
    DeclareLaunchArgument('x', default_value=['0'],
        description='x position'),
    DeclareLaunchArgument('y', default_value=['0'],
        description='y position'),
    DeclareLaunchArgument('z', default_value=['0'],
        description='z position'),
    DeclareLaunchArgument('yaw', default_value=['0'],
        description='yaw position'),

    DeclareLaunchArgument('bridge', default_value='true',
                          choices=['true', 'false'],
                          description='Run bridges'),
    DeclareLaunchArgument('world', default_value='basic_map',
                          description='GZ World'),
    DeclareLaunchArgument('spawn_model', default_value='true',
                          choices=['true', 'false'],
                          description='Spawn B3RB Model'),
    DeclareLaunchArgument('use_sim_time', default_value='true',
                          choices=['true', 'false'],
                          description='Use sim time'),
    DeclareLaunchArgument('log_level', default_value='error',
                          choices=['info', 'warn', 'error'],
                          description='log level'),
]


def generate_launch_description():

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([PathJoinSubstitution(
            [get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py'])]),
        launch_arguments=[('gz_args', [
            LaunchConfiguration('world'), '.sdf', ' -v 0', ' -r'
            ])]
    )

    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='bridge_gz_ros_clock',
        output='screen',
        condition=IfCondition(LaunchConfiguration('bridge')),
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time')
            }],
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
    )

    lidar_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='bridge_gz_ros_lidar',
        output='screen',
        condition=IfCondition(LaunchConfiguration('bridge')),
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time')
        }],
        arguments=[
            '/world/default/model/b3rb/link/lidar_link/sensor/lidar/scan' +
             '@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan'
        ],
        remappings=[
            ('/world/default/model/b3rb/link/lidar_link/sensor/lidar/scan',
             '/scan')
        ])

    wheel_odom_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='bridge_gz_ros_wheel_odom',
        output='screen',
        condition=IfCondition(LaunchConfiguration('bridge')),
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time')
            }],
        arguments=[
            '/world/default/model/b3rb/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model'
            ])

    wheel_odom_throttle = Node(
        package='topic_tools',
        executable='throttle',
        arguments=['messages', '/world/default/model/b3rb/joint_state', '100', '/cerebri/in/wheel_odometry'],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        )
    
    imu_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='bridge_gz_ros_imu',
        output='screen',
        condition=IfCondition(LaunchConfiguration('bridge')),
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time')
            }],
        arguments=[
            '/world/default/model/b3rb/link/sensors/sensor/imu_sensor/imu@sensor_msgs/msg/Imu[gz.msgs.IMU'
            ],
        remappings=[
            ('/world/default/model/b3rb/link/sensors/sensor/imu_sensor/imu', '/cerebri/in/imu')
            ])


    mag_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='bridge_gz_ros_mag',
        output='screen',
        condition=IfCondition(LaunchConfiguration('bridge')),
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time')
            }],
        arguments=[
            '/world/default/model/b3rb/link/sensors/sensor/mag_sensor/magnetometer@sensor_msgs/msg/MagneticField[gz.msgs.Magnetometer'
            ],
        remappings=[
            ('/world/default/model/b3rb/link/sensors/sensor/mag_sensor/magnetometer', '/cerebri/in/magnetic_field')
            ])

    nav_sat_fix_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='bridge_gz_ros_nav_sat_fix',
        output='screen',
        condition=IfCondition(LaunchConfiguration('bridge')),
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time')
            }],
        arguments=[
            '/world/default/model/b3rb/link/sensors/sensor/navsat_sensor/navsat@sensor_msgs/msg/NavSatFix[gz.msgs.NavSat'
            ],
        remappings=[
            ('/world/default/model/b3rb/link/sensors/sensor/navsat_sensor/navsat', '/cerebri/in/nav_sat_fix')
            ])

    battery_state_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='bridge_gz_ros_battery_state',
        output='screen',
        condition=IfCondition(LaunchConfiguration('bridge')),
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time')
            }],
        arguments=[
            '/model/b3rb/battery/linear_battery/state@sensor_msgs/msg/BatteryState[gz.msgs.BatteryState'
            ],
        remappings=[
            ('/model/b3rb/battery/linear_battery/state', '/cerebri/in/battery_state')
            ])

    actuator_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='bridge_gz_ros_actuator',
        output='screen',
        condition=IfCondition(LaunchConfiguration('bridge')),
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time')
            }],
        arguments=[
            '/actuators@actuator_msgs/msg/Actuators]gz.msgs.Actuators'
            ])

    actuator_relay = Node(
        package='topic_tools',
        executable='relay',
        arguments=['/cerebri/out/actuators', '/actuators'],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        arguments=[
            '-world', 'default',
            '-name', 'b3rb',
            '-x', LaunchConfiguration('x'),
            '-y', LaunchConfiguration('y'),
            '-z', LaunchConfiguration('z'),
            '-Y', LaunchConfiguration('yaw'),
            '-file', PathJoinSubstitution([get_package_share_directory(
                'b3rb_gz_resource'),
                'models/b3rb/model.sdf'])
        ],
        output='screen',
        condition=IfCondition(LaunchConfiguration("spawn_model")))

    # Define LaunchDescription variable
    return LaunchDescription(ARGUMENTS + [
        gz_sim,
        clock_bridge,
        lidar_bridge,
        wheel_odom_bridge,
        wheel_odom_throttle,
        #imu_bridge,
        #mag_bridge,
        #nav_sat_fix_bridge,
        battery_state_bridge,
        actuator_bridge,
        actuator_relay,
        spawn_robot,
    ])
