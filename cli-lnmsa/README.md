# CLI-LNMSA

## Overview

This script's objective is to make LibreNMS API calls accessible via CLI, and provide some basic output and filtering functionality.

## Deficiencies
- POST,PATCH, and PUT functions currently don't work because logic to pull the object being set out of parameters hasn't been written.

## Usage

Basic command structure
```
lnmsa <api function> <parameters>
```

Find Top ifInOctets for a device's ports
```
lnmsa get_port_graphs <device-id> columns=ifInOctets_rate,ifName,ifAlias --sort ifInOctets_rate
```
View Available functions
```
lnmsa
```
View lnmsa help
```
lnmsa --help
```

## Requirements
Python Libraries:
- click
- pandas
- rich


## Setup

Download `lnmsa.py` as `lnmsa`, Make the script executable `chmod +x lnmsa`.

## Troubleshooting

Some common issues:

- Ensure the API token has required permissions for call

## License

This script is released under the GNU License. See `LICENSE` for more details.
