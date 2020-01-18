# Lightwave TRV Integration for Homeassistant

This adds support for Thermostatic Radiator Valves (TRVs) to the LighwaveRF integration into Homeassistant.  
This is for Series 1 Lightwave

## Getting Started

Lightwave does not provide an interface, via the API, to query the Lightwave Hub for the current TRV status.  Instead the status is broadcast to the LAN.
Thus this integration comes in two coponents.  A Homeassistant custom configurations, and a proxy.
The proxy captures the TRV broadcast messages, and makes then avaiable to a Homeassistant polling loop.

### Installing

Copy this repro to your local machine.

Copy the folder, and all its contents to the Homeassistant configuration area.
```
cp -r customer_components ~homeassistant/.homeassistant
```


## Configuration
The TRV boradcasts its status with the device serial number as the only identifier.
This needs to be put into the HA configuration file.
The file *sample_configuration.yaml* gives an example.
```
lightwave:
  host: 192.168.10.10    	# Lightwave Hub
  trv_proxy_ip: 127.0.0.1       # Proxy address, do not change unless runing on a different server
  trv_proxy_port: 7878		# Do not change, unless a port clash
  lights:
    R99D1:
      name: Bedroom Light
  trv:				
    R1Dh:			# The ID of the TRV.  
				# This needs to be precise, see the existig HA documents on Lightwave
				# on how to find this
      name: Bedroom TRV
      serial: E84902		# Serial number of the TRV - found in the Lightwave App, or web site
```
If you wish to also get access to the TRV battery status, the add the following.
The identifier (R1Dh) and serial should be *identical* to the trv config, except for the name:
```
  battery:			# 
    R1Dh:
      name: Bedroom TRV battery
      serial: E84902
```
## lightwave.py
A modificaation is required to 
```
lib/python3.7/site-packages/lightwave/lightwave.py
```
to add TRV support.
To replace the file...
```
sudo cp lightwave/lighwave.py <PATH>/lib/python3.7/site-packages/lightwave/lightwave.py
```
Replace ```<PATH>``` to the appropriate homeassistant folder.

## Run the proxy
The proxy is (by default) configured to run on the same server as HA.
No configuration should be needed.   Simply run it...
```
python3 lwproxy.py &
```
You will need to configure this so it survives reboots etc.   I personally use "forever".
```
apt-get install forever
forever start python3 lwproxy.py
```

## Test
Restart hass.  (A restart is required, simply re-reading config is not sufficient)

## Authors

* **Colin Robbins** - *Initial work* - [ColinRobbins](https://github.com/ColinRobbins)

## License

This project is licensed under the same term as HomeAssistant - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgements

* [GeoffAtHome](https://github.com/GeoffAtHome) for the inital work that started me investigating how to do this!
