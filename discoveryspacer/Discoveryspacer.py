from lib.LibreNMSAPIClient import LibreNMSAPIClient
import time
import random
libreapi=LibreNMSAPIClient()

hours_to_take=6  #Change this to your discovery interval

deviceids=[]
for dev in libreapi.list_devices():
    deviceids.append(dev['device_id'])
time_to_wait=(hours_to_take * 3600) / len(deviceids)
print("Waiting " + str(time_to_wait) + " between devices to complete in about " + str(hours_to_take) + " hours")
random.shuffle(deviceids)
counter=0
for did in deviceids:
    libreapi.i_discover_device(did)
    counter=counter + 1
    print("Starting discovery for " + str(did) + " ["+ str(counter) + "/" + str(len(deviceids)) +"]")
    time.sleep(time_to_wait)
print("Finished!")
