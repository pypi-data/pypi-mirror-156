# Copyright (c) 2022 Red Hat Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import copy
import pprint

import pidet


class DataParser(object):
    def __init__(self, hostname, intervals=False, sockets=False):
        self.intervals = intervals
        self.sockets = sockets
        self.hostname = hostname
        if pidet.DEBUG:
            self.pp = pprint.PrettyPrinter(width=60, underscore_numbers=True)

    def _create_dict(self, data, socket_num=None):
        p = {}
        p['measurement'] = str(data['start']['connecting_to']['host'] + '-' +
                               str(data['start']['connecting_to']['port']))
        p['tags'] = {}
        p['tags']['hostname'] = self.hostname
        p['tags']['num_streams'] = data['start']['test_start']['num_streams']
        p['tags']['protocol'] = data['start']['test_start']['protocol']
        p['tags']['duration'] = data['start']['test_start']['duration']
        p['tags']['blksize'] = data['start']['test_start']['blksize']
        p['tags']['blocks'] = data['start']['test_start']['blocks']
        p['tags']['bytes'] = data['start']['test_start']['bytes']
        p['tags']['role'] = ('sender' if data['end']['sum_sent']['sender']
                             else 'receiver')
        p['tags']['sender_tcp_congestion'] = data['end'][
                'sender_tcp_congestion']
        p['tags']['receiver_tcp_congestion'] = data['end'][
                'receiver_tcp_congestion']
        p['tags']['runtime'] = data['end']['sum_sent']['end']
        p['time'] = int(data['start']['timestamp']['timesecs'] +
                        int(data['end']['sum_sent']['end'])) * 1000
        p['fields'] = {}
        p['fields']['sum_sent_bytes'] = data['end']['sum_sent']['bytes']
        p['fields']['retransmits'] = data['end']['sum_sent']['retransmits']
        p['fields']['sum_received_bytes'] = data['end']['sum_received'][
                'bytes']
        p['fields']['cpu_host_total'] = data['end'][
                'cpu_utilization_percent']['host_total']
        p['fields']['cpu_host_user'] = data['end'][
                'cpu_utilization_percent']['host_user']
        p['fields']['cpu_host_system'] = data['end'][
                'cpu_utilization_percent']['host_system']
        p['fields']['cpu_remote_total'] = data['end'][
                'cpu_utilization_percent']['remote_total']
        p['fields']['cpu_remote_system'] = data['end'][
                'cpu_utilization_percent']['remote_system']
        p['fields']['cpu_remote_user'] = data['end'][
                'cpu_utilization_percent']['remote_user']
        if socket_num:
            p['measurement'] += '-{}'.format(socket_num)
            p['tags']['socket_num'] = socket_num
            p['fields']['stream_send_bytes'] = data['end']['stream']['sender'][
                    'bytes']
            p['fields']['stream_retransmits'] = data['end']['stream'][
                    'sender']['retransmits']
            p['fields']['stream_rec_bytes'] = data['end']['stream'][
                    'receiver']['bytes']
            p['fields']['max_rtt'] = data['end']['stream']['sender'][
                    'max_rtt']
            p['fields']['mean_rtt'] = data['end']['stream']['sender'][
                    'mean_rtt']
            p['fields']['min_rtt'] = data['end']['stream']['sender']['min_rtt']

        if pidet.DEBUG:
            print("iperf3/parser:DataParser - _create_dict - output")
            self.pp.pprint(p)
        return p

    def parse_perf_obj(self, data):
        data_points = []
        if self.sockets:
            for stream in data['end']['streams']:
                blop = copy.deepcopy(data)
                blop['end'].pop('streams', None)
                blop['end']['stream'] = stream
                soc = blop['end']['stream']['socket']
                data_points.append(self._create_dict(blop, socket_num=soc))
        else:
            data_points.append(self._create_dict(data))
        return data_points
