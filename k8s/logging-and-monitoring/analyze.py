# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

"""
A little Python script to do some analysis of the NGINX logs.
To get the relevant NGINX logs:
1. Go to the OMS Portal
2. Create a new Log Search
3. Use a search string such as:

Type=ContainerLog Image="bigchaindb/nginx_3scale:1.3" GET NOT("Go-http-client") NOT(runscope)

(This gets all logs from the NGINX container, only those with the word "GET",
excluding those with the string "Go-http-client" [internal Kubernetes traffic],
excluding those with the string "runscope" [Runscope tests].)

4. In the left sidebar, at the top, use the dropdown menu to select the time range,
e.g. "Data based on last 7 days". Pay attention to the number of results and
the time series chart in the left sidebar. Are there any spikes?
5. Export the search results. A CSV file will be saved on your local machine.
6. $ python3 analyze.py logs.csv

Thanks to https://gist.github.com/hreeder/f1ffe1408d296ce0591d
"""

import sys
import csv
import re
from dateutil.parser import parse


lineformat = re.compile(r'(?P<ipaddress>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - '
                        r'\[(?P<dateandtime>\d{2}\/[a-z]{3}\/\d{4}:\d{2}:\d{2}:\d{2} '
                        r'(\+|\-)\d{4})\] ((\"(GET|POST) )(?P<url>.+)(http\/1\.1")) '
                        r'(?P<statuscode>\d{3}) '
                        r'(?P<bytessent>\d+) '
                        r'(["](?P<refferer>(\-)|(.+))["]) '
                        r'(["](?P<useragent>.+)["])',
                        re.IGNORECASE)

filepath = sys.argv[1]

logline_list = []
with open(filepath) as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    for row in csvreader:
        if row and (row[8] != 'LogEntry'):
            # because the first line is just the column headers, such as 'LogEntry'
            logline = row[8]
            print(logline + '\n')
            logline_data = re.search(lineformat, logline)
            if logline_data:
                logline_dict = logline_data.groupdict()
                logline_list.append(logline_dict)
                # so logline_list is a list of dicts
                # print('{}'.format(logline_dict))

# Analysis

total_bytes_sent = 0
tstamp_list = []

for lldict in logline_list:
    total_bytes_sent += int(lldict['bytessent'])
    dt = lldict['dateandtime']
    # https://tinyurl.com/lqjnhot
    dtime = parse(dt[:11] + " " + dt[12:])
    tstamp_list.append(dtime.timestamp())

print('Number of log lines seen: {}'.format(len(logline_list)))

# Time range
trange_sec = max(tstamp_list) - min(tstamp_list)
trange_days = trange_sec / 60.0 / 60.0 / 24.0
print('Time range seen (days): {}'.format(trange_days))

print('Total bytes sent: {}'.format(total_bytes_sent))

print('Average bytes sent per day (out via GET): {}'.
      format(total_bytes_sent / trange_days))
