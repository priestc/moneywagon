#!/usr/bin/env python

import sys
import argparse
import pkg_resources

from moneywagon import service_table
from moneywagon.supply_estimator import write_blocktime_adjustments

from subprocess import call

parser = argparse.ArgumentParser()
parser.add_argument('--minor', action='store_true', help='Make minor release.')
parser.add_argument('--major', action='store_true', help='Make major release.')
parser.add_argument('--point', action='store_true', help='Make point release.')
parser.add_argument('--do-blocktime-adjustments', default=True, action='store_true', help='Skip calculating blocktime adjustments')

argz = parser.parse_args()

if not argz.do_blocktime_adjustments:
    write_blocktime_adjustments("moneywagon/blocktime_adjustments.py", random=True)

ex_major, ex_minor, ex_point = pkg_resources.get_distribution('moneywagon').version.split(".")
version = "%s.%s.%s"

if argz.major:
    version = version % (int(ex_major) + 1, "0", "0")
elif argz.minor:
    version = version % (ex_major, int(ex_minor) + 1, "0")
elif argz.point:
    version = version % (ex_major, ex_minor, int(ex_point) + 1)

with open("setup.py", 'w') as f, open("setup_template.py") as t:
    setup = t.read().replace("{{ version }}", version)
    f.write(setup)

with open("README.md", 'w') as f, open("README_template.md") as t:
    table = service_table(format='html')
    readme = t.read().replace("{{ service_table }}", table)
    f.write(readme)

call(["python", "setup.py", "sdist", "upload"])
call(["python", "setup.py", "develop"])
