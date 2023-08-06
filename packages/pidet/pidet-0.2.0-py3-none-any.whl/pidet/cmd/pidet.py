# Copyright 2022 Red Hat Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Command-line interface to ingest performance data into InfluxDB.
"""

import argparse
import configparser
import copy
import json
import os
from pathlib import Path
import platform
import pprint
import sys

from oslo_utils import encodeutils

import pidet
from pidet.fio.parser import DataParser as FioParser
from pidet.influxdb.writer import Writer
from pidet.iperf3.parser import DataParser as IperfParser


class PidetShell(object):

    def get_parser(self):
        parser = argparse.ArgumentParser(
            prog='pidet',
            description=__doc__.strip(),
            epilog='Try "pidet help" for help',
            formatter_class=HelpFormat,
        )

        parser.add_argument('-d', '--debug',
                            default=False,
                            action='store_true',
                            help="Super verbose for debugging.")
        parser.add_argument('-v', '--verbose',
                            default=False,
                            action='store_true',
                            help='Verbose output of what is going on.')
        parser.add_argument('-c', '--config',
                            default=str(Path.home()) + '/.config/pidet.ini',
                            help='Config file to be used instead of cmd args.')
        parser.add_argument('-b', '--bucket',
                            dest='influxdb_bucket',
                            help=('Which InfluxDB bucket the data will be '
                                  'saved into.'))
        parser.add_argument('-o', '--org',
                            dest='influxdb_org',
                            help='The InfluxDB org to be used.')
        parser.add_argument('-t', '--token',
                            dest='influxdb_token',
                            help='Authentication token for InfluxDB.')
        parser.add_argument('-u', '--url',
                            dest='influxdb_url',
                            help='Url to the InfluxDB instance.')
        parser.add_argument('-f', '--file',
                            help=('The performance data to be parsed. '
                                  'This can also be supplied via stdin.'))
        parser.add_argument('--host_name',
                            default=platform.node(),
                            help=('"host" tag used to store the info. '
                                  'Defaults to system hostname.'))
        parser.add_argument('--version',
                            action='version',
                            version=pidet.__version__)
        return parser

    def get_perfdata(self, options):
        if options.file:
            return open(options.file, 'r')
        try:
            os.fstat(0)
        except OSError:
            return
        if not sys.stdin.isatty():
            if hasattr(sys.stdin, 'buffer'):
                return sys.stdin.buffer
            return sys.stdin
        return

    def main(self, argv):
        parser = self.get_parser()
        argv_initial = copy.deepcopy(argv)
        (options, args) = parser.parse_known_args(argv_initial)
        if os.access(options.config, os.R_OK):
            config = configparser.ConfigParser()
            config.read(options.config)
            parser.set_defaults(**config['default'])
            (options, args) = parser.parse_known_args(argv)
            if options.debug:
                pidet.DEBUG = True
                self.pp = pprint.PrettyPrinter(width=60,
                                               underscore_numbers=True)
                self.pp.pprint(options)
            if options.verbose:
                pidet.VERBOSE = True

        perfdata = self.get_perfdata(options)
        if not perfdata:
            parser.print_help()
            fail("No input data available.")
        try:
            perf_obj = json.loads(perfdata.read())
        except Exception as e:
            fail(e)

        if pidet.DEBUG:
            self.pp.pprint(perf_obj)

        if perf_obj.get('start', {}).get('version', '').startswith('iperf'):
            dp = IperfParser(options.host_name)
        elif perf_obj.get('fio version', None):
            dp = FioParser(options.host_name)
        else:
            fail("Input data not recognized.")
        points = dp.parse_perf_obj(perf_obj)
        if not (points and points[0]):
            fail("We have no data.")
        if pidet.DEBUG or pidet.VERBOSE:
            print("Writing %i records." % len(points))
        writer = Writer(options)
        writer.write_point_list(points)


class HelpFormat(argparse.HelpFormatter):
    def start_section(self, heading):
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(HelpFormat, self).start_section(heading)


def fail(e, exitcode=99):
    sys.stderr.write("ERROR: %s\n" % str(e))
    sys.exit(exitcode)


def main():
    try:
        argv = [encodeutils.safe_decode(arg) for arg in sys.argv[1:]]
        PidetShell().main(argv)
    except KeyboardInterrupt:
        fail("... Pidet interrupted by user", exitcode=130)
    except Exception as e:
        fail(e)


if __name__ == '__main__':
    main()
