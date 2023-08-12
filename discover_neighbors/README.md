# LibreNMS Neighbor Discovery Script

## Overview

This script uses the LibreNMS API to find unknown neighbor devices and their connections.

It retrieves device and link information from the API and compares local and remote hostnames to identify unknown neighbors. The script prints out a list of any neighbors that don't match a known local device.

## Usage

```
python script.py [hostname]
```

Running the script without any arguments will print all unknown neighbors.

You can filter the results by passing a partial or full hostname as an argument. This will print only unknown neighbors matching that hostname.

The script also prints out the local device and port connected to each unknown neighbor.

## Requirements

- Python 3
- LibreNMS with API enabled
- API token with read privileges 

## Configuration

The script expects the API URL and token to be specified in a `.env` file in the format:

```
LIBRENMS_URL=http://librenms.example.com
LIBRENMS_TOKEN=abcdef123456
```

## Logging

Logs from the script will be written to `/var/log/librenms_neighbors.log` by default. The log directory can be customized by setting the `LOG_DIR` environment variable.

## Troubleshooting

Some common issues:

- Make sure the API URL and token in `.env` are correct
- Check for connectivity issues reaching the LibreNMS API
- Try increasing the request timeout if API calls are timing out
- Ensure the API token has required permissions to access devices and links
- Check the log file for errors contacting the API

## License

This script is released under the GNU License. See `LICENSE` for more details.