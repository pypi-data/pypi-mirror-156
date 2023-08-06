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
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS


class Writer(object):
    def __init__(self, options):
        try:
            self.url = options.influxdb_url
            self.token = options.influxdb_token
            self.org = options.influxdb_org
            self.bucket = options.influxdb_bucket
        except AttributeError:
            raise

    def write_point_list(self, points, write_precision='ms'):
        with influxdb_client.InfluxDBClient(url=self.url,
                                            token=self.token,
                                            org=self.org) as client:
            write_api = client.write_api(write_options=SYNCHRONOUS)
            write_api.write(bucket=self.bucket, org=self.org,
                            record=points,
                            write_precision=write_precision)
