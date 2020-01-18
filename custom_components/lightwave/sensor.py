"""Support for LightwaveRF TRV - Battery."""
import asyncio
import json
import logging
import socket

from homeassistant.const import CONF_NAME
from homeassistant.helpers.entity import Entity

from . import LIGHTWAVE_LINK, LIGHTWAVE_TRV_PROXY, LIGHTWAVE_TRV_PROXY_PORT

logger = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Find and return battery."""
    if not discovery_info:
        return

    batt = []

    trv_proxy_ip = hass.data[LIGHTWAVE_TRV_PROXY]
    trv_proxy_port = hass.data[LIGHTWAVE_TRV_PROXY_PORT]
    
    for device_id, device_config in discovery_info.items():
        name = device_config[CONF_NAME]
        serial = device_config['serial']
        batt.append(LWRF_Battery(name, device_id,serial,trv_proxy_ip, trv_proxy_port))

    async_add_entities(batt)

class LWRF_Battery(Entity):
    """TRV Battery"""

    def __init__( self, name, device_id,serial,trv_proxy_ip, trv_proxy_port):
        """Initialize the sensor."""
        self._name = name
        self._device_id = device_id
        self._state = None
        self._serial = serial
        self._device_class = "battery"
        self._proxy_ip = trv_proxy_ip
        self._proxy_port = trv_proxy_port

    @property
    def should_poll(self):
        """Connect to the TRV proxy"""
        return True

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._device_class

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def update(self):
        """Communicate with a Lightwave RTF Proxy to get state"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(2.0)
                msg = self._serial.encode('UTF-8')
                sock.sendto(msg, (self._proxy_ip,self._proxy_port))
                response, addr = sock.recvfrom(1024)
                msg =response.decode()
                j = json.loads(msg)
                if "batt" in j.keys():
                    self._state = j["batt"]
                if "error" in j.keys():
                    logger.warning("TRV proxy error: %s",j["error"])

        except Exception as ex:
            logger.warning("TRV updater error %s",ex)
