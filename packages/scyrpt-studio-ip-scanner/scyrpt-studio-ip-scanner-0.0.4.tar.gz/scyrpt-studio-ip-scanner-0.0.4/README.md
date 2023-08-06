# ip-scanner
Pip package to scan IP address on local ip range.

It scans all ip addresses on specified range and port/s and returns the list of live IP addresses.

### Installation
You can install the IP Scanner from PyPI:
```
python -m pip install scyrpt-studio-ip-scanner
```

IP Scanner is supported on Python 3.8 and above.

### How to use

There are 2 ways to use this library -

1. Start IP scanning from command line. To do that, simply run -
```
ip_scanner <<First 3 parts of IP>> <<Ports (Can be multiple, separated by comma)>> <<Start IP Address>> <<End IP Address>>

Ex. - ip_scanner "192.168.1." "80" "5" "15" 
Will scan IP's from 192.168.1.5 to 192.168.1.15 on Port 80
```

2. Import in your code and scan/trigger it via your code -
```
from ip_scanner.ip_scanner import IPScanner

ipScanner = IPScanner(base_ip="192.168.1.", ports=(80, ), start_ip=5, end_ip=15)
ipScanner.start_scanning()
```
It returns a list of live IP addresses found in the specified range