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

import os

from testtools.matchers import (
    DirExists,
    FileExists
)

import integration_tests


class TarPluginTestCase(integration_tests.TestCase):

    def test_stage_nil_plugin(self):
        project_dir = 'simple-tar'
        self.run_snapcraft('stage', project_dir)

        expected_files = [
            'flat',
            os.path.join('flatdir', 'flat2'),
            'onedeep',
            os.path.join('onedeepdir', 'onedeep2'),
            'oneflat',
            'top-simple',
            'notop',
            'parent',
            'slash',
            'readonly_file'
        ]
        for expected_file in expected_files:
            self.assertThat(
                os.path.join(project_dir, 'stage', expected_file),
                FileExists())
        expected_dirs = [
            'dir-simple',
            'notopdir',
        ]
        for expected_dir in expected_dirs:
            self.assertThat(
                os.path.join(project_dir, 'stage', expected_dir),
                DirExists())

        binary_output = self.get_output_ignoring_non_zero_exit(
            os.path.join('stage', 'bin', 'test'), cwd=project_dir)
        self.assertEqual('tarproject\n', binary_output)

        # Regression test for
        # https://bugs.launchpad.net/snapcraft/+bug/1500728
        self.run_snapcraft('pull', project_dir)
