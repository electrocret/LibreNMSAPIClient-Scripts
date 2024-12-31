# Discovery Spacer

## Overview

This script spaces out device discoveries over your discovery interval. On large Librenms deployments, overtime device discoveries can get bunched together causing interruptions in polling & long polling times due to SQL DB locks.

## Usage

Execute script

## Requirements

No additional libraries are needed beyond LibreNMS API Client. All libraries this script uses are standard python packages.

## Setup

Edit 'hours_to_take' variable to your instances polling interval.

## Troubleshooting

Outline possible problems that can occur with the script and how to fix them.

## License

This script is released under the GNU License. See `LICENSE` for more details.
