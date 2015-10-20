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

import glob
import logging
import os

import snapcraft
import snapcraft.common
import snapcraft.plugins.jdk


logger = logging.getLogger(__name__)


class MavenPlugin(snapcraft.plugins.jdk.JdkPlugin):

    @classmethod
    def schema(cls):
        schema = super().schema()
        schema['properties']['maven-options'] = {
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
        self.build_packages.append('maven')

    def build(self):
        super().build()

        if not self.run(['mvn', 'package'] + self.options.maven_options):
            return False
        jarfiles = glob.glob(os.path.join(self.builddir, 'target', '*.jar'))
        warfiles = glob.glob(os.path.join(self.builddir, 'target', '*.war'))
        if not (jarfiles or warfiles):
            logger.error('Could not find any built jar or war files for '
                         'part %s', self.name)
            snapcraft.common.fatal()
        if jarfiles:
            jardir = os.path.join(self.installdir, 'jar')
            os.makedirs(jardir, exist_ok=True)
            if not self.run(['cp', '-a'] + jarfiles + [jardir]):
                return False
        if warfiles:
            wardir = os.path.join(self.installdir, 'war')
            os.makedirs(wardir, exist_ok=True)
            if not self.run(['cp', '-a'] + warfiles + [wardir]):
                return False
        return True
