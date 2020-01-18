import asyncio
import json

trv = {}

PROXY_IP = '127.0.0.1'
PROXY_PORT = 7878
LW_PORT = 9761

class trv_collector:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        stripped = message[2:]
        data = json.loads(stripped)
        if "serial" in data.keys():
            serial = data["serial"]
            trv[serial] = stripped
	
class trv_responder:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        if message in trv.keys():
             reply = trv[message]
        else:
             reply = '{"error":"trv ' + message + ' not found"}'
        self.transport.sendto (reply.encode("UTF-8"),addr)

loop = asyncio.get_event_loop()

print("Starting UDP servers")

# One protocol instance will be created to serve all client requests
collect = loop.create_datagram_endpoint( trv_collector, local_addr=('0.0.0.0', LW_PORT))
collect_transport, collect_proto = loop.run_until_complete(collect)

respond = loop.create_datagram_endpoint( trv_responder, local_addr=(PROXY_IP,PROXY_PORT))
respond_transport, respond_proto = loop.run_until_complete(respond)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

collect_transport.close()
respond_transport.close()

loop.close()
