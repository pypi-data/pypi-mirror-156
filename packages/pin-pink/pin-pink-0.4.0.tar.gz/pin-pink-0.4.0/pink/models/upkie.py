#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 Stéphane Caron
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
`Upkie`_ is a homemade wheeled biped robot that can balance, crouch and turn
around. It proudly stands on broomsticks and 3D printed parts (^_^)

.. _Upkie: https://hackaday.io/project/185729-upkie-wheeled-biped-robot
"""

import os

import pinocchio as pin


def build_upkie_from_urdf(urdf_path: str) -> pin.RobotWrapper:
    """
    Build the Upkie model from its URDF.

    Args:
        urdf_path: Path to the URDF in `upkie_description`_.

    .. _upkie_description: https://github.com/tasts-robots/upkie_description
    """
    abspath = os.path.abspath(os.path.dirname(urdf_path) + "/..")
    return pin.RobotWrapper.BuildFromURDF(
        filename=os.path.join(abspath, "urdf", "upkie.urdf"),
        package_dirs=[os.path.dirname(abspath)],
        root_joint=pin.JointModelFreeFlyer(),
    )
