# Author : Doeraene Anthony

import asyncio
import argparse
import ssl

from aioquic.asyncio.client import connect
from aioquic.quic.configuration import QuicConfiguration
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.events import QuicEvent, StreamDataReceived
from aioquic.quic.congestion import QuicCongestionControl, K_MAX_DATAGRAM_SIZE, K_LOSS_REDUCTION_FACTOR, K_INITIAL_WINDOW, CongestionEvent
from aioquic.quic.congestion.cubic import CubicCongestionControl
from aioquic.quic.congestion.reno import RenoCongestionControl
from aioquic.quic.congestion.bbr import BBRCongestionControl
from aioquic.quic.congestion.bbr2 import BBR2CongestionControl
from aioquic.quic.logger import QuicLogger
from aioquic.quic.congestion.slow_starts import HyStart
from typing import cast
from socket import gethostname
from struct import pack

from time import sleep
from qlog_parser import write_qlogs, add_name

data = None
debug=0
hostname = gethostname()
local_port = None
count_lost = 0


def get_attribute(cc : QuicCongestionControl, field) -> str:
    if (field == "congestion_window"):
        return F"Cwnd = {cc.get_congestion_window()}"
    if (field == "ssthresh"):
        return F"ssthresh = {cc.get_ssthresh()}"
    return F"{field} = {cc.__getattribute__(field)}"

def print_cc_details(cc : QuicCongestionControl, fields = "all"):
    """
    Print details about the state of the CCA
    Note that this function will only print details if the debug level of the program is at least of 2 (see the verbosity argument)
    """
    if (debug < 2):
        return
    if fields == "all":
        print(get_attribute(cc, "congestion_window"))
        print(get_attribute(cc, 'ssthresh'))
        print(F"MSS = {K_MAX_DATAGRAM_SIZE}")
        print(F"Loss Reduction Factor = {K_LOSS_REDUCTION_FACTOR}")
        print(F"Initial Window = {K_INITIAL_WINDOW}")
    elif isinstance(fields, list):
        mapped = map(lambda x : get_attribute(cc, x), fields)
        print(", ".join(mapped))
    else:
        print(get_attribute(cc, fields))

def callback(event, cc : QuicCongestionControl):
    if (event == CongestionEvent.ACK):
        print_cc_details(cc, ["congestion_window", "ssthresh"])
    if (event == CongestionEvent.PACKET_LOST):
        global count_lost
        count_lost += 1
        if (debug >= 1):
            print(F"Packet lost by {hostname}:{local_port} (total lost : {count_lost})!")
        print_cc_details(cc, ["congestion_window", "ssthresh"])

class ClientHandler(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.waiter = None
        self.cc = self._quic._loss._cc

        print_cc_details(self.cc)

    def send_again(self, n, stream_id) -> None:
        print("Sending in 10s...")
        sleep(10)
        self._quic.send_stream_data(stream_id, n)
        self._quic.send_stream_data(stream_id, data, end_stream=True)
        self.transmit()

    async def send_data(self) -> None:
        stream_id = self._quic.get_next_available_stream_id()

        waiter = self._loop.create_future()
        self.waiter = waiter

        l = len(data)
        n = pack("!i", l)
        self._quic.send_stream_data(stream_id, n)
        self._quic.send_stream_data(stream_id, data, end_stream=True)
        self.transmit()

        # used to test the cubic-bug (cwnd explosion after some idle time)
        #threading.Thread(target=self.send_again, args=(n, stream_id)).start() 

        return waiter

    def quic_event_received(self, event: QuicEvent) -> None:
        if self.waiter is not None and isinstance(event, StreamDataReceived):
            waiter = self.waiter
            self.waiter = None
            waiter.set_result(event.data)

async def main(host, port, local_port, conf, output, name):
    try:
        if debug == 1:
            print("Starting client...")
        async with connect(host, port, configuration=conf, local_port=local_port, create_protocol=ClientHandler) as client:
            if debug == 1:
                print(F"Connected to server on {host}:{str(port)}!")
            client = cast(ClientHandler, client)
            res = await client.send_data()
            await res
            if debug == 1:
                print(F"Received {res.result()}")
            if output:
                qlogs = conf.quic_logger.to_dict()
                add_name(qlogs, name)
                write_qlogs(qlogs, output)
    except Exception as e:
        if debug:
            raise e
        

parser = argparse.ArgumentParser(
                    prog='Quic client',
                    description='Start a quic client that will send the content of a file to a server')

parser.add_argument('filename', help="The name of the file containing the data to be sent")           # positional argument
parser.add_argument('--host', default="127.0.0.1", help="The ip address of the server")
parser.add_argument("-p", '--port', default=8080, type=int, help="The port on which the server is listening")
parser.add_argument("-l", '--local-port', default=8081, type=int, help="The src port on which the request should be sent")
parser.add_argument("-c", '--cca', default="reno", help="The congestion control algorithm to be used (default to 'reno'). Currently available cca are 'reno', 'cubic', 'bbr' and 'bbr2'")
parser.add_argument('-v', '--verbose', type=int, default=0, help="Verbosity of the program, going from 0 to 2 (0 = no info, 1 = info on the state of client, 2 = info on the state of congestion control)")  # on/off flag
parser.add_argument("--keylog-file", type=str, default=None, help="Path to a file where the secrets should be saved (to be used in wireshark)")
parser.add_argument("--log-dir", type=str, default=None, help="Path to a dir where the logs will be saved")
parser.add_argument("-s", "--size-cwnd", type=int, default=None, help="Size for a static cwnd (only when cca == nothing)")
parser.add_argument("-n", "--name", type=str, default="", help="Name of the scenario used, save it in qlogs as the 'name_client' field (only applied when a log-dir field is provided)")
parser.add_argument("--reno-friendly", action="store_true", help="Whether to use a reno friendly region (default to False) (only applied when using a cubic cca)")

args = parser.parse_args()

with open(args.filename, "br") as file:
    data = file.read()

debug = args.verbose
local_port = args.local_port

cca = None
if (args.cca == "reno"):
    cca = RenoCongestionControl(callback=callback, slow_start=HyStart())
elif (args.cca == "cubic"):
    cca = CubicCongestionControl(callback=callback, reno_friendly_activated=args.reno_friendly)
elif (args.cca == "bbr"):
    cca = BBRCongestionControl(callback=callback)
elif (args.cca == "bbr2"):
    cca = BBR2CongestionControl(callback=callback)
elif (args.cca == "nothing"):
    
    if args.size_cwnd != None:
        cca = QuicCongestionControl(callback=callback, fixed_cwnd=args.size_cwnd)
    else:
        cca = QuicCongestionControl(callback=callback)
else:
    print("Invalid congestion control algorithm : can't find this algorithm")
    exit(1)

conf = QuicConfiguration(alpn_protocols=["quic-testing"], is_client=True, congestion_control=cca)
conf.verify_mode = ssl.CERT_NONE
if args.keylog_file != None:
    conf.secrets_log_file = open(args.keylog_file, "a")

if (args.log_dir):
    conf.quic_logger = QuicLogger()

asyncio.run(main(args.host, args.port, args.local_port, conf, args.log_dir, args.name))
