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
    def __init__(self, hostname, iops=True, throughput=True, latency=False):
        self.iops = iops
        self.throughput = throughput
        self.latency = latency
        self.hostname = hostname
        if pidet.DEBUG:
            self.pp = pprint.PrettyPrinter(width=60, underscore_numbers=True)

    def _create_dict(self, jobnum, data):
        p = {}
        p['measurement'] = data['global options']['name']
        p['tags'] = {}
        p['tags']['hostname'] = self.hostname
        p['tags']['job_number'] = jobnum
        p['tags']['job_name'] = data['job']['jobname']
        p['tags']['rw'] = data['global options']['rw']
        p['tags']['rwmixread'] = data['global options']['rwmixread']
        p['tags']['rwmixwrite'] = data['global options']['rwmixwrite']
        p['tags']['runtime'] = data['global options']['runtime']
        p['tags']['ioengine'] = data['job']['job options']['ioengine']
        p['tags']['iodepth'] = data['job']['job options']['iodepth']
        p['tags']['block_size'] = data['global options']['bs']
        p['time'] = int(data['timestamp_ms'])
        p['fields'] = {}
        p['fields']['drop_read_ios'] = data['job']['read']['drop_ios']
        p['fields']['drop_write_ios'] = data['job']['write']['drop_ios']
        p['fields']['total_read_ios'] = data['job']['read']['total_ios']
        p['fields']['total_write_ios'] = data['job']['write']['total_ios']
        p['fields']['sys_cpu'] = data['job']['sys_cpu']
        p['fields']['usr_cpu'] = data['job']['usr_cpu']
        if self.iops:
            p['fields']['read_iops'] = data['job']['read']['iops']
            p['fields']['read_iops_max'] = data['job']['read']['iops_max']
            p['fields']['read_iops_mean'] = data['job']['read']['iops_mean']
            p['fields']['read_iops_min'] = data['job']['read']['iops_min']
            p['fields']['write_iops'] = data['job']['write']['iops']
            p['fields']['write_iops_max'] = data['job']['write']['iops_max']
            p['fields']['write_iops_mean'] = data['job']['write']['iops_mean']
            p['fields']['write_iops_min'] = data['job']['write']['iops_min']
        if self.throughput:
            p['fields']['read_kbytes'] = data['job']['read']['io_kbytes']
            p['fields']['write_kbytes'] = data['job']['write']['io_kbytes']

        if pidet.DEBUG:
            print("fio/parser:DataParser - _create_dict - output")
            self.pp.pprint(p)
        return p

    def parse_perf_obj(self, data):
        data_points = []
        job_number = 0
        for job in data['jobs']:
            blop = copy.deepcopy(data)
            blop.pop('jobs', None)
            blop['job'] = job
            data_points.append(self._create_dict(job_number, blop))
            job_number += 1
        return data_points
