"""Lightwave TRV Proxy."""
import asyncio
import getopt
import json
import sys

TRV = {}

DEFAULT_PROXY_IP = "127.0.0.1"
DEFAULT_PROXY_PORT = 7878
LW_PORT = 9761


class TrvCollector:
    """UDP proxy to collect Lightwave traffic."""

    def __init__(self, verbose):
        """Initialise Collector entity."""
        self.transport = None
        self.verbose = verbose

    def connection_made(self, transport):
        """Start the proxy."""
        self.transport = transport

    # pylint: disable=W0613, R0201
    def datagram_received(self, data, addr):
        """Manage receipt of a UDP packet from Lightwave."""
        message = data.decode()
        if self.verbose:
            print(message)
        stripped = message[2:]
        data = json.loads(stripped)
        if "serial" in data.keys():
            serial = data["serial"]
            TRV[serial] = stripped


class TrvResponder:
    """UDP Listner, for connections from HomeAssistant."""

    def __init__(self, verbose):
        """Initialise Responder entity."""
        self.transport = None
        self.verbose = verbose

    def connection_made(self, transport):
        """Start the listner."""
        self.transport = transport

    def datagram_received(self, data, addr):
        """Respond to query from HomeAssistant."""
        message = data.decode()
        if self.verbose:
            print(message)
        if message in TRV.keys():
            reply = TRV[message]
        else:
            reply = '{"error":"trv ' + message + ' not found"}'
            if self.verbose:
                print("Not found")
        self.transport.sendto(reply.encode("UTF-8"), addr)


def proxy(proxy_ip, port, verbose):
    """Run the LW Proxy."""
    loop = asyncio.get_event_loop()

    if verbose:
        print(f"Starting UDP servers: {proxy_ip}:{port} & 0.0.0.0:{LW_PORT}")

    # One protocol instance will be created to serve all client requests
    collect = loop.create_datagram_endpoint(
        lambda: TrvCollector(verbose), local_addr=("0.0.0.0", LW_PORT)
    )
    collect_transport, dummy = loop.run_until_complete(collect)

    respond = loop.create_datagram_endpoint(
        lambda: TrvResponder(verbose), local_addr=(proxy_ip, port)
    )
    respond_transport, dummy = loop.run_until_complete(respond)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    collect_transport.close()
    respond_transport.close()

    loop.close()


def main(argv=None):
    """Start the proxy."""
    if argv is None:
        argv = sys.argv[1:]

    proxy_ip = DEFAULT_PROXY_IP
    proxy_port = DEFAULT_PROXY_PORT
    verbose = False

    try:
        opts, dummy = getopt.getopt(argv, "hvi:p:", ["proxy_ip=", "proxy_port="])
    except getopt.GetoptError:
        print("lwproxy.py -i proxy_ip_address -p proxy_port -v")
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print("lwproxy.py -i proxy_ip_address -p proxy_port -v")
            sys.exit()
        elif opt in ("-i", "--proxy_ip"):
            proxy_ip = arg
        elif opt in ("-p", "--proxy_port"):
            proxy_port = arg
        elif opt in ("-v", "--verbose"):
            verbose = True

    proxy(proxy_ip, proxy_port, verbose)


if __name__ == "__main__":
    main()
