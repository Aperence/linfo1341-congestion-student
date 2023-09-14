# Author : Doeraene Anthony

import asyncio
import argparse

from aioquic.asyncio.server import serve
from aioquic.quic import events
from aioquic.quic.configuration import QuicConfiguration
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.events import StreamDataReceived, DatagramFrameReceived, QuicEvent
from aioquic.quic.logger import QuicFileLogger
from socket import ntohl
from struct import unpack

debug=0

class ServerProtocol(QuicConnectionProtocol):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clients = {}

    def quic_event_received(self, event: QuicEvent) -> None:
        if isinstance(event, StreamDataReceived):
            if not event.stream_id in self.clients:
                self.clients[event.stream_id] = {"length" : unpack("!i", event.data[:4])[0] + 4, "received" : 0}
            self.clients[event.stream_id]["received"] += len(event.data)
            received = self.clients[event.stream_id]["received"]
            length = self.clients[event.stream_id]["length"]
            if debug == 1: print(F'Received data {received}/{length} B ({received / length * 100:.2f}%) stream ({event.stream_id})')
            if debug >= 2: print(F'Received data = "{event.data}"')
            if event.end_stream:
                print(F"End of stream ({event.stream_id})")
                self._quic.send_stream_data(event.stream_id, b"ok", end_stream=True)

async def main(host, port, conf):

    await serve(host, port, configuration=conf, create_protocol=ServerProtocol)

    if debug >= 1:
        print(F"Server running on {host}:{port}!")
    
    await asyncio.Future()

conf = QuicConfiguration(alpn_protocols=["quic-testing"], is_client=False)


parser = argparse.ArgumentParser(
                    prog='Quic client',
                    description='Start a quic client that will send the content of a file to a server')


parser.add_argument('--host', default="127.0.0.1", help="The ip address on which the server will listen")
parser.add_argument("-p", '--port', default=8080, type=int, help="The port on which the server will listen")
parser.add_argument("-c", '--cert', default="./certs/cert.pem", help="The certificate that should be used with the quic server")
parser.add_argument("-k", '--key', default="./certs/key.pem", help="The key that is used alongside the certificate")
parser.add_argument('-v', '--verbose', type=int, default=0, help="Verbosity of the program, going from 0 to 2")  # on/off flag
parser.add_argument("--log-dir", type=str, default=None, help="Path to a dir where the logs will be saved")

args = parser.parse_args()

conf.load_cert_chain(args.cert, args.key)

debug = args.verbose

if (args.log_dir):
    conf.quic_logger = QuicFileLogger(args.log_dir)

try:
    asyncio.run(main(args.host, args.port, conf))
except KeyboardInterrupt:
    exit(0)