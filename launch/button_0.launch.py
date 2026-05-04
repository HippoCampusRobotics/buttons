# Copyright (C) 2022-2023 Thies Lennart Alff

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

from ament_index_python.packages import get_package_share_path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def declare_launch_args(launch_description: LaunchDescription):
    action = DeclareLaunchArgument(name='vehicle_name')
    launch_description.add_action(action)

    action = DeclareLaunchArgument(name='use_manipulator')
    launch_description.add_action(action)


def generate_launch_description():
    pkg = 'buttons'
    package_path = get_package_share_path(pkg)
    button_config_file = str(package_path / 'config/button_0.yaml')

    launch_description = LaunchDescription()
    declare_launch_args(launch_description=launch_description)
    path = str(get_package_share_path(pkg) / 'launch/generic_button.launch.py')
    source = PythonLaunchDescriptionSource(path)
    action = IncludeLaunchDescription(
        source,
        launch_arguments={
            'namespace': 'button_0',
            'vehicle_name': LaunchConfiguration('vehicle_name'),
            'button_config_file': button_config_file,
            'use_manipulator': LaunchConfiguration('use_manipulator')
        }.items(),
    )
    launch_description.add_action(action)

    return launch_description
