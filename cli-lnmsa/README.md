# CLI-LNMSA

## Overview

This script's objective is to make LibreNMS API calls accessible via CLI, and provide some basic display and filtering functionality.

## Deficiencies
- POST,PATCH, and PUT functions currently don't work because logic to pull the object being set hasn't been written.

## Usage

```
lnmsa <api function> <parameters>
```

```
lnmsa get_port_graphs 8 columns=ifInOctets_rate,ifName,ifAlias --sort ifInOctets_rate
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
