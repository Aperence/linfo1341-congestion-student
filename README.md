# QUIC and Congestion Control Lab

This [Kathara](https://www.kathara.org/) lab will allow students to get handson experience with congestion control schemes using the QUIC protocol.

## Installation requirements

- Docker : can be installed easily by following the instructions on their [main site](https://docs.docker.com/get-docker/). Note that on Linux, you should install the [Docker Engine](https://docs.docker.com/engine/install/), while on Windows it is preferable to install [Docker desktop](https://docs.docker.com/desktop/install/windows-install/) 
  
- [Kathara](https://www.kathara.org/) : to install it, just follow the guide on their site, or the guide on the [wiki](https://github.com/KatharaFramework/Kathara/wiki)

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

By default, the qlogs are stored in the file /lab/shared/NAME_SCEN/LOG_ID where LOG_ID is a randomly generated identifier. A script to parse these files is provided in [src/qlog_parser.py](src/qlog_parser.py).

We use qlogs during this lab, as the plotter uses them to represent the variation of fields.

During this lab, you can also disable the generation of qlogs if you want to check whether they have impact on the performance. To do so, simply remove the argument `--log-dir` when running a client/server. You can also modify the scenarios if you want to.

## Running the pre-made scenarios

To run the scenarios, simply open a terminal in this folder. Type the following command:

### For Linux/Mac
```bash
./start
cd lab && sudo kathara connect main
```
### For Windows
```bash
.\start.bat
cd lab
kathara connect main
```

This will run the lab, and should after some time open a terminal as `root@main`. This terminal will be the main hub where you'll be able to run the different scenarios, as well as connect to the other devices if you want to play by yourself with the congestion control.

### Run on Vagrant (not recommended):
If you encounter issues when trying to run the lab and are unable to make it work, you can try running it with Vagrant. To do so, first, install Vagrant and a VM provider (VirtualBox or VMWare for example). Then, run the following commands that will create a fedora VM:

```bash
# create the vm
# note : you may need to pass your provider
# --provider=virtualbox or --provider=vmware
vagrant up  

# connect to the vm
vagrant ssh

# You are now inside the vm, run the lab
cd /vagrant
./start
cd lab && sudo kathara connect main
```

Note that for plotting, you'll need to copy files from the VM to your local computer, and then use the plotting scripts. To do so, just use the `copy_from_vm.sh` script (if you are on Windows, simply use the `scp` command). It will probably ask you for a password, for this VM it is simply `vagrant`.

---

You can now follow the instructions contained in the [lab README](lab/README.md) to learn how to run the different scenarios, and observe the evolution of congestion control variables over time. You may want to use wireshark or tcpdump to analyze captured packets though during this lab. For this, simply follow the instructions in the [wireshark section](#sniffing-packets-using-wireshark) below.

To shut down the lab, use the command 
```bash
exit # Alternatively, use CTRL+D
```
to quit the main hub, and type one of the following commands:
### For Linux/Max
```bash
./clean 
```
### For Windows
```bash
.\clean.bat
```
### For vagrant
```bash
# Exit the the main device + the vm and run the following commands
vagrant destroy
# remove the create files by copy_from_vm.sh
rm -rf lab/shared  
``` 
to remove all the files created by the lab.

### Lab on Red-hat based distributions

On these kind of distributions, the lab requires the firewall to be disabled (as it won't work at all otherwise). The start script will automatically ask you if you want to disable it, and will proceed with this disabling. After having done the lab, the cleaning script will ask you wether you want to enable your firewall once again. If you want to handle these tasks manually, you can use :
```bash
# restart the firewall
sudo systemctl start firewalld  
# stop the firewall
sudo systemctl stop firewalld   
```

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

## Acknowledgments
Thanks to Olivier Bonaventure, Maxime Piraux, François Michel, Louis Navarre and Aurelien Buchet who allowed me to realize this project, and gave feedback along the development of this project, allowing me to improve it even further!

