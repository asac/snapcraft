# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright (C) 2015 Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""The kernel plugin refines the generic kbuild plugin to allow building
kernel snaps with all the bells and whistles in one shot...

The following kernel specific options are provided by this plugin:

    - kernel-image-type:
      (string)
      the kernel image type to build; maps to make target. default: "bzImage"

"""

import os
import snapcraft
import multiprocessing
import snapcraft.plugins.kbuild


class KernelPlugin(snapcraft.plugins.kbuild.KBuildPlugin):

    @classmethod
    def schema(cls):
        schema = super().schema()

        schema['properties']['kernel-image-type'] = {
            'type': 'string',
            'default': 'bzImage',
        }

        return schema

    def __init__(self, name, options):
        super().__init__(name, options)
        self.make_targets = [ self.options.kernel_image_type ]
        self.make_install_targets = [ "modules_install" ]

    def do_install(self):
        super().do_install()
