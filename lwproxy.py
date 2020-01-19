"""Lightwave TRV Proxy."""
import asyncio
import json

TRV = {}

PROXY_IP = "127.0.0.1"
PROXY_PORT = 7878
LW_PORT = 9761


class TrvCollector:
    """UDP proxy to collect Lightwave traffic."""

    def __init__(self):
        """Initialise Collector entity."""
        self.transport = None

    def connection_made(self, transport):
        """Start the proxy."""
        self.transport = transport

    # pylint: disable=W0613, R0201
    def datagram_received(self, data, addr):
        """Manage receipt of a UDP packet from Lightwave."""
        message = data.decode()
        stripped = message[2:]
        data = json.loads(stripped)
        if "serial" in data.keys():
            serial = data["serial"]
            TRV[serial] = stripped


class TrvResponder:
    """UDP Listner, for connections from HomeAssistant."""

    def __init__(self):
        """Initialise Responder entity."""
        self.transport = None

    def connection_made(self, transport):
        """Start the listner."""
        self.transport = transport

    def datagram_received(self, data, addr):
        """Respond to query from HomeAssistant."""
        message = data.decode()
        if message in TRV.keys():
            reply = TRV[message]
        else:
            reply = '{"error":"trv ' + message + ' not found"}'
        self.transport.sendto(reply.encode("UTF-8"), addr)


LOOP = asyncio.get_event_loop()

print("Starting UDP servers")

# One protocol instance will be created to serve all client requests
COLLECT = LOOP.create_datagram_endpoint(
    TrvCollector,
    local_addr=("0.0.0.0", LW_PORT)
)
COLLECT_TRANSPORT, DUMMY = LOOP.run_until_complete(COLLECT)

RESPOND = LOOP.create_datagram_endpoint(
    TrvResponder,
    local_addr=(PROXY_IP, PROXY_PORT)
)
RESPOND_TRANSPORT, DUMMY = LOOP.run_until_complete(RESPOND)

try:
    LOOP.run_forever()
except KeyboardInterrupt:
    pass

COLLECT_TRANSPORT.close()
RESPOND_TRANSPORT.close()

LOOP.close()
