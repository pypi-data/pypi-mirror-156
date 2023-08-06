# pidet

Python client for passing perf data to InfluxDB.

## Installation
`pip install pidet`

## Usage
`pidet --bucket <your data bucket> --org <your org> --token <your token> --url <url to InfluxDB> [--file <data json file>] or < <data json file>`

You can also pipe the output directly to pidet:
`fio --output-format=json /path/to/jobfile | pidet -c /path/to/pidet.ini`

Using ini-style config file, by default pidet is looking from ~/.config/pidet.ini. Different config file location can be supplied with '-c' or '--config' <FILE> argument. The command line arguments override values in the config file.

```ini
[default]
influxdb_bucket = fio
influxdb_org = myorg
influxdb_url = http://influx.example.com:8086
influxdb_token = YOUR_TOKEN
```

So `pidet --bucket another -c ./pidet.ini` with above example would result data stored in the "another" bucket under myorg with YOUR_TOKEN.

pidet will autodetect iperf3 output. `iperf3 -J -c <Server IP> | pidet` when ~/.config/pidet.ini is setup correctly.

## Supported perf tools
fio
iperf3

## Roadmap
Expand supported tools from fio.

## License
Apache Software License 2.0

## Project status
Beta
