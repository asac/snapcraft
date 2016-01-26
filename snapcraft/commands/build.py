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

"""
snapcraft build

Build parts.

Usage:
  build [options] [PART ...]

Options:
  -j [<threads>]        multi threaded build for plugins that support it; use 0 for cpu-count+1 [default: 0]
  -V                    verbose built for plugins that support it.
  -h --help             show this help message and exit.

"""

from docopt import docopt

from snapcraft import lifecycle
from snapcraft import common

def main(argv=None):
    argv = argv if argv else []
    args = docopt(__doc__, argv=argv)

    common.set_build_threads(args['-j'])
    common.set_verbose(args['-V'])

    lifecycle.execute('build', args['PART'])
