"""Python library to provide reliable communication link with LightWaveRF lights and switches."""
import logging
import socket
import time
from itertools import cycle
from queue import Queue
from threading import Thread

_LOGGER = logging.getLogger(__name__)


class LWLink():
    """LWLink provides a communication link with the LightwaveRF hub."""

    SOCKET_TIMEOUT = 2.0
    RX_PORT = 9761
    TX_PORT = 9760

    link_ip = None
    transaction_id = cycle(range(1, 1000))
    the_queue = Queue()
    thread = None

    def __init__(self, link_ip=None):
        """Initialise the component."""
        if link_ip is not None:
            LWLink.link_ip = link_ip

    def _send_message(self, msg):
        """Add message to queue and start processing the queue."""
        LWLink.the_queue.put_nowait(msg)
        if LWLink.thread is None or not LWLink.thread.isAlive():
            LWLink.thread = Thread(target=self._send_queue)
            LWLink.thread.start()

    def register(self):
        """Create the message to register client."""
        msg = '!F*p'
        self._send_message(msg)

    def deregister_all(self):
        """Create the message to deregister all clients."""
        msg = '!F*xP'
        self._send_message(msg)

    def turn_on_light(self, device_id, name):
        """Create the message to turn light on."""
        msg = "!%sFdP32|Turn On|%s" % (device_id, name)
        self._send_message(msg)

    def turn_on_switch(self, device_id, name):
        """Create the message to turn switch on."""
        msg = "!%sF1|Turn On|%s" % (device_id, name)
        self._send_message(msg)

    def turn_on_with_brightness(self, device_id, name, brightness):
        """Scale brightness from 0..255 to 1..32."""
        brightness_value = round((brightness * 31) / 255) + 1
        # F1 = Light on and F0 = light off. FdP[0..32] is brightness. 32 is
        # full. We want that when turning the light on.
        msg = "!%sFdP%d|Lights %d|%s" % (
            device_id, brightness_value, brightness_value, name)
        self._send_message(msg)

    def turn_off(self, device_id, name):
        """Create the message to turn light or switch off."""
        msg = "!%sF0|Turn Off|%s" % (device_id, name)
        self._send_message(msg)

    def set_temperature(self, device_id,  temp, name):
        """Create the message to set the trv target temp."""
        msg = '321,!%sF*tP%s|Set Target|%s' % (device_id, round(temp,1), name)
        self._send_message(msg)

    def _send_queue(self):
        """If the queue is not empty, process the queue."""
        while not LWLink.the_queue.empty():
            self._send_reliable_message(LWLink.the_queue.get_nowait())

    def _send_reliable_message(self, msg):
        """Send msg to LightwaveRF hub."""
        result = False
        max_retries = 15
        trans_id = next(LWLink.transaction_id)
        msg = "%d,%s" % (trans_id, msg)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) \
                    as write_sock, \
                    socket.socket(socket.AF_INET, socket.SOCK_DGRAM) \
                    as read_sock:
                write_sock.setsockopt(
                    socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                read_sock.setsockopt(
                    socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                read_sock.setsockopt(socket.SOL_SOCKET,
                                     socket.SO_BROADCAST, 1)
                read_sock.settimeout(self.SOCKET_TIMEOUT)
                read_sock.bind(('0.0.0.0', self.RX_PORT))
                while max_retries:
                    max_retries -= 1
                    write_sock.sendto(msg.encode(
                        'UTF-8'), (LWLink.link_ip, self.TX_PORT))
                    result = False
                    while True:
                        response, dummy = read_sock.recvfrom(1024)
                        response = response.decode('UTF-8')
                        if "Not yet registered." in response:
                            _LOGGER.error("Not yet registered")
                            self.register()
                            result = True
                            break

                        if response.startswith("%d,OK" % trans_id):
                            result = True
                            break
                        if response.startswith("%d,ERR" % trans_id):
                            _LOGGER.error(response)
                            break

                        _LOGGER.info(response)

                    if result:
                        break

                    time.sleep(0.25)

        except socket.timeout:
            _LOGGER.error("LW broker timeout!")
            return result

        except Exception as ex:
            _LOGGER.error(ex)
            raise

        if result:
            _LOGGER.info("LW broker OK!")
        else:
            _LOGGER.error("LW broker fail!")
        return result
