#!/usr/bin/python

#  LibreNMS Neighbor Discovery Script
#  
#  @author Skylark (github.com/LoveSkylark)
#  @license GPL

import os
import sys
import logging.handlers
import argparse
from dotenv import load_dotenv

# Get project root 
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from lib.LibreNMSAPIClient.LibreNMSAPIClient import LibreNMSAPIClient

def setup_logging(log_dir):

    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'librenms_device_inventory.log')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s:%(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=5*1024*1024,
                backupCount=10
            )
        ]
    )

def parse_args():
    parser = argparse.ArgumentParser(description="Script to download LibreNMS configuration")
    parser.add_argument("hostname", nargs="?", help="Hostname to filter on")
    return parser.parse_args()

def get_api_data(lnms):
    try:
        devices = lnms.list_devices()
        links = lnms.list_links()
        ports = lnms.get_all_ports()
    except Exception as e:
        logging.error(f"Error calling API: {e}")
        sys.exit(1)
    
    logging.info("API call succeeded")
    return devices, links, ports

def list_unknown_neighbors(args, devices, links, ports):
    neighbours = find_unknown_neighbors(devices, links)
    # Get the list of unknown neighbors
    for neighbour in neighbours:
        logging.info(f"Neighbour {neighbour} discovered")

        # If no hostname argument is given, print all unknown neighbors
        if not args.hostname:
            print(neighbour)
                
        # If a hostname argument is given, print matching neighbors and their port information
        elif neighbour.startswith(args.hostname):
            print(neighbour)
            for device_name, port_name in get_sorted_port_list(args.hostname, devices, links, ports):
                print(f"  -> {device_name} ({port_name})")

def find_unknown_neighbors(devices, links):

    # Create a set of all local and remote device short names in lowercase
    local_match = set(i['sysName'].lower().split('.', 1)[0] for i in devices if isinstance(i, dict))
    remote_match = set(i['remote_hostname'].lower().split('(', 1)[0].split('.', 1)[0] for i in links if isinstance(i, dict))
    
    # Compute the set difference between the two sets to find remote hostnames that don't have a matching local device name
    reply = sorted(list(remote_match - local_match))
    
    return reply

def get_sorted_port_list(hostname, devices, links, ports):

    reply = []
    
    for link in links:

        # Check if the remote hostname of the link matches the specified hostname
        if hostname in link['remote_hostname'].lower().split('.', 1)[0]:
        
            # Retrieve the device name associated with the local device ID of the link
            device_name = next((device['sysName'] for device in devices if device['device_id'] == link['local_device_id']), None)
        
            # Retrieve the port name associated with the local port ID of the link
            port_name = next((port['ifName'] for port in ports if port['port_id'] == link['local_port_id']), None)
            reply.append((device_name, port_name))
    
    # Sort the 'reply' list by the device name in ascending order (case-insensitive)
    reply.sort(key=lambda x: x[0].lower() if x[0] else '')
    return reply

def print_help(args):
    if not args.hostname:
        print()
        print("Add hostname to narrow list")
        print("Examples:")
        print("     ./lnms_unknown 'partial-or-full-hostname'")

def main():

    # Load environment variables
    load_dotenv()

    # Setup logging
    log_dir = os.path.join('..', os.environ.get('log_dir', 'var/log/'))
    setup_logging(log_dir)

    # Parse command line arguments
    args = parse_args()

    # Create API client
    lnms = LibreNMSAPIClient()

    # Get data from API
    devices, links, ports = get_api_data(lnms)

    
    # Print results
    list_unknown_neighbors(args, devices, links, ports)

    # Print help text
    print_help(args)

if __name__ == "__main__":
    main()