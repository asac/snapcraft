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

    - kernel-initrd-mods:
      (array of string)
      list of modules to include in initrd; note that kernel snaps do not
      provide the core bootlogic which comes from snappy Ubuntu Core
      OS snap. Include all modules you need for mounting rootfs here.

    - kernel-initrd-comp:
      (string; default: gz)
      initrd compression to use; values supported: none, gz, bz2, xz

    - kernel-image-path:
      (string)
      path to the kernel image that got built; will be copied to vmlinuz

"""

import os
import shutil
import snapcraft
import multiprocessing
import snapcraft.plugins.kbuild
import logging

logger = logging.getLogger(__name__)

class KernelPlugin(snapcraft.plugins.kbuild.KBuildPlugin):

    @classmethod
    def schema(cls):
        schema = super().schema()

        schema['properties']['kernel-image-target'] = {
            'type': 'string',
            'default': 'bzImage',
        }

        schema['properties']['kernel-initrd-mods'] = {
            'type': 'array',
            'minitems': 0,
            'uniqueItems': True,
            'items': {
                'type': 'string',
            },
            'default': [],
        }

        schema['properties']['kernel-initrd-comp'] = {
            'type': 'string',
            'default': 'gz',
        }

        schema['properties']['kernel-image-path'] = {
            'type': 'string',
            'default': "kernel.py:kernel-image-path/NOT/SET",
        }

        return schema

    def __init__(self, name, options):
        super().__init__(name, options)
        self.make_targets = [ self.options.kernel_image_target ]
        self.make_install_targets = [ "modules_install", "INSTALL_MOD_PATH="+self.installdir ]

    def make_initrd(self):
        logger.info ("generating driver initrd for kernel release: "+self.kernel_release)

        modprobe_out = self.run_output (['modprobe', '-n', '--show-depends', '-d',
                                         self.installdir, '-S', self.kernel_release]
                                        + self.options.kernel_initrd_mods)
        modprobe_outs = modprobe_out.split(os.linesep)

        inc_modules = []
        for l in modprobe_outs:
            inc_modules.append(l[l.rfind('lib/modules/'+self.kernel_release):])

        inc_modules.extend(['lib/modules/'+self.kernel_release+'/modules.dep',
                            'lib/modules/'+self.kernel_release+'/modules.dep.bin'])

        logger.info ("modprobe out: " + str(inc_modules))

        # XXX: make this use the configured compress algo from options
        self.run_raw(['sh -c "echo \''+ '\n'.join(inc_modules)+'\'' +
                      '| cpio -o | gzip -c > initrd-mods-'+self.kernel_release+'"'],
                     cwd=self.installdir)

    def parse_kernel_release(self):
        kernel_release_path = os.path.join (self.builddir, "include/config/kernel.release")
        self.kernel_release = ""

        with open(kernel_release_path, "r") as f:
            self.kernel_release = f.read().strip()
            f.close()

        if self.kernel_release == "":
            raise Error("no kernel release version info found at " + kernel_release_path)

    def copy_vmlinuz(self):
        src = os.path.join(self.builddir, self.options.kernel_image_path)
        dst = os.path.join(self.installdir, "vmlinuz-"+self.kernel_release)
        if not os.path.exists(src):
            raise Error("kernel build did not output a vmlinux binary in top level dir")
        shutil.copyfile (src, dst)

    def copy_system_map(self):
        src_system_map = os.path.join(self.builddir, "System.map")
        if not os.path.exists(src_system_map):
            raise Error("kernel build did not output a vmlinux binary in top level dir")
        self.run_raw(['cat', src_system_map, ' > System.map-'+self.kernel_release], cwd=self.installdir)


    def do_install(self):
        super().do_install()

        self.parse_kernel_release()
        self.make_initrd()
        self.copy_vmlinuz()
        self.copy_system_map()
