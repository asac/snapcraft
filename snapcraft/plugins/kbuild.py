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

"""The kbuild plugin is used for building kbuild based projects as snapcraft
parts.

The plugin applies your selected defconfig first by running

    make defconfig

and then uses the kconfigs flag to augment the resulting config by prepending
the configured kconfigs values to the .config and running

    "yes" "" | make oldconfig

to create an updated .config file.

If kconfigfile is provided this plugin will use the provided config file
wholesale as the starting point instead of make $kdefconfig. In case user
configures both a kdefconfig as well as kconfigfile, kconfigfile approach will
be used.

This plugin is based on the snapcraft.BasePlugin and supports the properties
provided by that plus the following kbuild specific options with semantics as
explained above:

    - kdefconfig:
      (string)
      defconfig target to use to see base configuration. default: "defconfig"

    - kconfigfile:
      (filepath)
      path to file to use as base configuration. If provided this option wins
      over kdefconfig. default: None

    - kconfigs
      (list of strings)
      explicit list of configs to force; this will override the configs that
      were set as base through kdefconfig and kconfigfile and dependent configs
      will be fixed using the defaults encoded in the kbuild config
      definitions.  If you dont want default for one or more implicit configs
      coming out of these, just add them to this list as well.

"""

import os
import snapcraft
from snapcraft import common


class KBuildPlugin(snapcraft.BasePlugin):

    @classmethod
    def schema(cls):
        schema = super().schema()

        schema['properties']['kdefconfig'] = {
            'type': 'string',
            'default': 'defconfig',
        }

        schema['properties']['kconfigfile'] = {
            'type': 'string',
            'default': None,
        }

        schema['properties']['kconfigs'] = {
            'type': 'array',
            'minitems': 1,
            'uniqueItems': True,
            'items': {
                'type': 'string',
            },
            'default': [],
        }

        return schema

    def __init__(self, name, options):
        super().__init__(name, options)
        self.build_packages.extend([
            'make',
        ])

        self.make_targets = []
        self.make_install_targets = ['install']

    def get_verbose_makeflags(self):
        if common.get_verbose():
            return ['V=1']
        return []

    def do_base_config(self, config_path):
        # if kconfigfile is provided use that
        # otherwise use defconfig to seed the base config
        if self.options.kconfigfile is None:
            # first run defconfig for setting baseline
            self.run(['make', self.options.kdefconfig]
                     + self.get_verbose_makeflags())
        else:
            os.copy(self.options.kconfigfile, config_path)

    def do_patch_config(self, config_path):
        # prepend the generated file with provided kconfigs
        #  - concat kconfigs to buffer
        #  - read current .config and append
        #  - write out to disk
        config = "\n".join(self.options.kconfigs)

        with open(config_path, "r") as f:
            config = config + "\n\n" + f.read()
            f.close()

        # note that prepending and appending the overrides seems
        # only way to convince all kbuild versions to pick up the
        # configs during oldconfig in .config
        config = config + "\n\n" + "\n".join(self.options.kconfigs)

        with open(config_path, "w") as f:
            f.write(config)
            f.close()

    def do_remake_config(self):
        # update config to include kconfig amendments using oldconfig
        self.run_raw(['\"yes\"', '\"\"', '|' 'make', 'oldconfig']
                     + self.get_verbose_makeflags())

    def do_build(self):
        # build the software
        self.run(['make',
                  '-j' + str(common.get_build_threads())]
                 + self.get_verbose_makeflags()
                 + self.make_targets)

    def do_install(self):
        # install to installdir
        self.run(['make', 'CONFIG_PREFIX='+self.installdir,
                  '-j' + str(common.get_build_threads())]
                 + self.get_verbose_makeflags()
                 + self.make_install_targets)

    def build(self):
        super().build()

        config_path = os.path.join(self.builddir, ".config")

        self.do_base_config(config_path)
        self.do_patch_config(config_path)
        self.do_remake_config()
        self.do_build()
        self.do_install()
