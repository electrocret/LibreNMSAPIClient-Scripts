# CLI-LNMSA

## Overview

This script's objective is to make LibreNMS API calls accessible via CLI, and provide some basic display and filtering functionality.

## Usage

```
lnmsa <api function> <parameters>
```

```
lnmsa get_port_graphs 8 columns=ifInOctets_rate,ifName,ifAlias --sort ifInOctets_rate
```



## Requirements

- Python 3
- LibreNMS with API enabled
- API token with read and write privileges (write is optional)


## Troubleshooting

Some common issues:

- Make sure the API URL and token in `.env` are correct
- Check for connectivity issues reaching the LibreNMS API
- Try increasing the request timeout if API calls are timing out
- Ensure the API token has required permissions for call

## License

This script is released under the GNU License. See `LICENSE` for more details.
