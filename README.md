# QUIC and Congestion Control Lab

This [Kathara](https://www.kathara.org/) lab will allow students to get handson experience with congestion control schemes using the QUIC protocol.

## Installation requirements

- Docker : can be installed easily by following the instructions on their [main site](https://docs.docker.com/get-docker/)
  
- [Kathara](https://www.kathara.org/) : to install it, just follow the guide on their site, or the guide on the [wiki](https://github.com/KatharaFramework/Kathara/wiki)

- If you are on a Red-Hat Based device, uncomment the line `67` of the [start](./start) script.

## Description of the lab

In this lab, you will learn how congestion control works the reason why these algorithms are part of today's Internet.
To do so, we will work on a quite simple configuration:

![](images/topology_student.drawio.png)

The clients send data to the server (upload of a file), but the link between the 2 routers is a bottleneck that has a limited bandwidth of only ~8Mbps. The two clients will need to share this link appropriately in order to be able to transmit at the same time.

During this lab, you observe:
- the problems that occur when there is no congestion control
- how congestion control reacts to packet losses
- how two clients can  fairly share a single bottleneck link
- how the round-trip time influences some congestion control schemes 
- how routers can also play a role in a fair share of a link (fair queuing)

This lab uses scenarios that will run transactions in specific conditions and to show you how the QUIC protocol and its congestion control algorithm reacts to these.

## Qlogs

In order to record the events in the different scenarios, the clients and servers are configured to log information using the QLOG format. The exact format is described in the [qlog IETF draft](https://datatracker.ietf.org/doc/draft-ietf-quic-qlog-main-schema/).

By default, the qlogs are stored the file /lab/shared/NAME_SCEN/LOG_ID where LOG_ID is a randomly generated identifier. A script to parse these file is provided in [src/qlog_parser.py](src/qlog_parser.py).

We use qlogs during this lab, as the plotter uses them to represent the variation of fields.

During this lab, you can also disable the generation of qlogs if you want to check whether they have impact on the performance. To do so, simply remove the argument `--log-dir` when running a client/server. You can also modify the scenarios if you want to.

## Running the pre-made scenarios

To run the scenarios, simply open a terminal in this folder. Type the following command:

```
./start
```

This will run the lab, and should after some time open a terminal as `root@main`. This terminal will be the main hub where you'll be able to run the differents scenarios, as well as connecting to the other devices if you want to play by yourself with the congestion control.

You can now follow the instructions contained in the [lab README](lab/README.md) to learn how to run the different scenarios, and observation the evolution of congestion control variables over time. You may want to use wireshark or tcpdump to analyze captured packets though during this lab. For this, simply follow the instructions of the [wireshark section](#sniffing-packets-using-wireshark) below.

To shutdown the lab, use the command 
```
exit
```
to quit the main hub, and type :
```
./clean
```
to remove all the files created by the lab

## Sniffing packets using wireshark

During these labs, you can use wireshark to sniff packets and see in real-time how QUIC works.

To do so, some (small) preparation is needed since QUIC packets are almost entirely encrypted.

First of all, launch the wireshark capture by going to [http://localhost:3000](http://localhost:3000), and start a capture on `eth0`.

After that, when starting a client, you will have to specify a log file for the secret keys. These keys will be needed in order to decode the messages exchanged during the communication. To do so, the only thing you need to do is specify a path to a file where these keys should be saved when lauching the client. We suggest you to save it in the `/shared` folder, as it will allow you to get it on your local device easily. For example:

```
python3 ./client.py ./scenarios/small_data.txt --keylog-file ../shared/log.txt
```

(Note: the step of saving the key is automatically done for you when running the scenarios, and will be saved in `lab/shared/keys.txt`)

Wait for the QUIC transaction to terminate.

Once the client stops, you can now go in Wireshark>Edit>Preferences>Protocols>TLS.

You'll end up on a screen similar to this: ![](images/tls_screen.png)

Here, paste the path of the log file you entered in the client earlier, in the field **(Pre)-Master-Secret log filename**. 

And that's it, everything is now configured and you will be able to see in clear the content of each packet exchanged during your transaction. Just be careful to always include the log-file argument when lauching the client from now on, otherwise you will not be able to decrypt the content of packets.

## Getting the answers

To get the answers of the lab, simply contact the teaching team of [linfo1341 course](https://uclouvain.be/cours-2023-linfo1341), on the official moodle page of the course if you have access to it, or directly by contacting them by email if you don't have an UCLouvain account.

## Acknowledgements
Thanks to Olivier Bonaventure, Maxime Piraux, François Michel, Louis Navarre and Aurelien Buchet who allowed me to realize this project, and gave feedback along the development of this project, allowing to improve it even further !

