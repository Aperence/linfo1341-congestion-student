# Running your tests in the lab

## Running the scenarios

To run a scenario, just run the command :
```
./scenarios/NAME_SCEN
```
with NAME_SCEN the name of the scenario.

Yes, it is as simple as that !

When a scenario has ended, you'll be able to plot the results of this scenario (not in the main device, but in another terminal) and see how everything went.

## Description of the scenarios

### [Without congestion control, good situation](../scenarios/no_cca_low_rate)
In this short transaction, we'll start by a simple example : what happens when we always transmit at a fixed rate (cwnd constant) ? With this much information, it might be difficult to know what will results from this, so let's add an hypothesis : the client sends at a rate of ~4Mbps. Try to think about what will happen, and when you're ready, run the `scenarios/no_cca_low_rate` file, and inspect the results using 
```
python3 src/qlog_parser.py lab/shared/no_cca_low_rate/LOG_ID.qlog -d
python3 src/plot_congestion.py lab/shared/no_cca_low_rate/ --dir -f delivery_rate
```

What do you observe ? Was there any problem during the transmission ?



### [Without congestion control, when the worst happen](../scenarios/no_cca_high_rate)

Now that we've seen what happens with a fixed cwnd transmitting at a lesser rate compared to the bottleneck bandwidth, let's see what happens when the rate is greater than bottleneck bandwidth. To do so, we'll transmit at a rate of 80Mbps, as we are quite impatient and we want the upload to be done faster (damn you human, why can't you wait a bit !). You can think about what might happen, and then run the `scenarios/no_cca_high_rate` file, and inspect the results using 
```
python3 src/qlog_parser.py lab/shared/no_cca_high_rate/LOG_ID.qlog -d
```

We'll also run a transmission with a cubic congestion control algorithm to be able to compare with it.

How did it performs compared to cubic ?



### [Starting simple : one client with CCA](../scenarios/cca_single)

After this quick introduction about why congestion control is important, let's see how they behave in (quite) real situations. To do so, you can run the script `scenarios/cca_single`, first with argument `reno` to observe a classical reno congestion control, and then with argument `cubic` to see the cubic version.

After that, you can check how the cwnd evolved by running :

```
python3 src/plot_congestion.py lab/shared/cca_single/reno --dir
python3 src/plot_congestion.py lab/shared/cca_single/cubic --dir
```

What are the main differences you see ?



### [Stepping up : sharing bandwidth](../scenarios/cca_share)

In the previous scenario, we have seen how each congestion control algorithm acts when it can use fully a link on its own. Let's see now what happen when 2 clients send data at the same time and have to share the ressources. You can try a reno-cubic, reno-reno and cubic-cubic transaction and see what happens.

Run the script `scenarios/cca_share` by passing as arguments the 2 congestion control used for the transmission.

After everything has run, you can see the evolution of cwnd by using the plot script and replacing cca1 and cca2 by the actual cca you passed in argument:
```
python3 src/plot_congestion.py lab/shared/cca_share/cca1_cca2 --dir
```

You can also inspect the delivery rates using the following commands:
```
python3 src/plot_congestion.py lab/shared/cca_share/cca1_cca2 --dir -f delivery_rate
python3 src/share_bandwidth.py lab/shared/cca_share/cca1_cca2
```

Is the bandwidth shared fairly ? And how does the cwnd of the 2 cca evolve ?



### [Sharring bandwidth : even for TCP flows](../scenarios/compare_iperf)

We've seen how 2 quic clients share the bandwidth. But in the real world, QUIC isn't the only transport protocol in use. Another one frequently used is TCP and you should know a plenty about it already. One question that you might ask yourself is <q>Does two seperate protocols allow the sharing of the same bandwidth ?</q>, and in this test, we'll answer this question. The client2 will run a TCP connection (using the iperf tool) and send data to server2, while client1 use a QUIC connection and send data to server1.

Run the script `scenarios/compare_iperf` by passing as argument the control congestion you want to use, feel free to select the one you prefer between cubic and reno.

After that, run the plotter by using and replace CCA by the one you selected:
```
python3 src/plot_congestion.py lab/shared/compare_iperf/CCA_iperf --dir
```

Check also the results of iperf, which prints how much time it took to run, as well as the bandwidth mesured during this time. What do you observe ? Do they share fairly the bandwidth, or does one flow take all the ressources for itself ?



### [When your neighbor doesn't want to share...](../scenarios/without_fair_queue)

Up to now, we've seen how you can use a cca to share bandwidth and have a fair repartition of ressources. But what should we do when someone has a faulty cca and/or doesn't want to share ressources. Many companies would want to be able to use the network alone without being bothered by the actions of other people. Let's see what happen when someone try to always send a too big amount of data, and how it affects the other people in the network.

To do so, run the script `scenarios/without_fair_queue` with cubic or reno, where the router has a simple LIFO queue as a buffer (drop the incoming packet if buffer full).

Run after that the plotter with the following command and see what happened (replace CCA by the congestion control you used):
```
python3 src/plot_congestion.py lab/shared/without_fair_queue/CCA --dir -f delivery_rate -l
```

What do you see ? Is that a fair share of the bandwidth ?



### [...but the router saves the day](../scenarios/fair_queue)

The end hosts aren't the only ones who can influence the rate of transmission in a network, and router may have a huge influence on the rate a flow may transmit. Perhaps, dropping the last packet arrived wasn't a good solution, so let's try using a fair queue. To do so, we'll add on router1 a fair queue as buffer, using the [`fq_codel`](https://man7.org/linux/man-pages/man8/tc-fq_codel.8.html) utilitary tool. This tool allow use to use a deficit round robin on different queues, and the incoming flows may be put in different queues based on the hash of their ip-port couple. Let's see now how the bandwidth is shared between the 2 hosts.

Run the script `scenarios/fair_queue` with cubic or reno.

Run after that the plotter, while replacing CCA by the congestion control you used:
```
python3 src/plot_congestion.py lab/shared/fair_queue/CCA --dir -f delivery_rate -l
```

What do you see ? Is this still as unfair ?



### [Effect of RTT on transmission rate](../scenarios/rtt_influence)

Up until now, we've seen how the different cca behave while having a constant RTT. A question we could ask ourselves is <q>Does the RTT have any influence on the transmit rate ?</q>. Let's answer this question in this scenario !

Run the `scenarios/rtt_influence` script, one time with reno, and the other time with cubic.

Plot the results using 
```
python3 src/plot_congestion.py lab/shared/rtt_influence/reno --dir -a
python3 src/plot_congestion.py lab/shared/rtt_influence/cubic --dir -a
```

What do you see ? Does Reno with a longer RTT takes more time to send the same amount of data ? How does it (or not) affect the growth of cwnd ? Same questions for cubic.



### [Wait, are you lagging ?](../scenarios/compare_long_rtt)

As the last scenario of this lab, we'll see how different congestion control behave when transmitting under long rtt conditions.

Run the `scenarios/compare_long_rtt cubic reno` script, and compare reno with cubic.

You can then plot the results using 
```
python3 src/plot_congestion.py lab/shared/compare_long_rtt/cubic_reno --dir -a
```

Which one does perform the best under long rtt situation ? Why is this the case ?



## Extra

### Running the scenarios with BBR/BBRv2

You can run all the above scenario who takes in argument a congestion control algorithm with bbr or bbrv2. These algorithms weren't verified and might have strange behaviours, but it might be interesting to experiment with a non loss-based cca.

### Connecting to the other devices

During the lab, you may want to have access to the clients, or the router to run some custom tests. To do this, you just have to run the command:
```
./connect DEV_NAME
```
with DEV_NAME is the name of the device you want to connect to.

For example, to connect to the router1 device, simply use 
```
./connect router1
```

### QUIC server

#### How to run the server manually

To run the server, you simply have to run the following command in the home directory of server1/2:

```
python3 src/server.py --host 10.0.1.X -v VERBOSITY
```

where 
- VERBOSITY is the level of verbosity you want ({0 = no output, 1 = minor explanations, 2 = full explanations on what is happening})
- X is the id of the device, for example, if you want to run the server on server1, X = 1, thus the host should be `10.0.1.1`

A more detailled explanations of the arguments can be found by running `python3 ./server.py -h`.

(Note: a server is automatically started on the server1 and server2 devices when the lab is started)

### QUIC client

#### How to run the client manually

In this lab, we will use the scenarios defined in the first section to show how quic congestion control works.
But you may want to test by yourself using a client, so here's how to run the client by your own.
To run the client, you simply have to run the following command in the home directory in client1/2:

```
python3 src/client.py FILENAME --host 10.0.1.X
```

where 
- FILENAME is the name of the file containing the data to be sent
- X is the id of the device running the server, for example if server1 is the server, X=1, thus the host should be `10.0.1.1`

Don't forget to add the `--keylog-file` argument if you want to use wireshark

Also, a more detailled explanation of the arguments can be found by running `python3 ./client.py -h`.

### Given scripts

#### [Plot_congestion.py](../src/plot_congestion.py)

This script is given to make plots of the different states updated during the quic transaction. To use it simply run the following command : 
```
python3 src/plot_congestion.py LOG_FILE
```
where LOG_FILE is the path to a qlog file generated by a client/server.

This scripts also has a load of options : 

- `-l` : whether to show the losses or not (default = show losses)
- `-s` : show a scatter instead of a plot
- `-W` : show the $W_{max}$ variable on plot (can only be used with cubic)
- `-f field` : the field of congestion control you want to plot (default = cwnd). For example, to plot in BBR the evolution of the `pacing_gain`, simply put the option `-f pacing_gain`. You can check the different fields using `qlog_parser.py` with the `--list-fields` option
- `-d step_time` and `-m step_field` : define when there shouldn't be a line drawn between 2 points of the same phase. In practice, it is rare to use these arguments.
- `--dir` : consider the the LOG_FILE is a directory and all qlogs contained in this directory will be plotted (not recursive)
- `-a` : align the graphs such that they each start at time 0
- `--reno-friendly` : use a reno friendly region for cubic

You can also specify more than one log_file when running this script, and if more than one file is given, each one of these will be plotted on a different subplot, allowing to compare the evolution of the state of multiple client at the same time. (for example, compare the evolution of cwnd of 2 clients sending data on the same link)

More details can be found by using the `-h` flag.

#### [Qlog_parser.py](../src/qlog_parser.py)

This file contains methods to open and filter the qlog files. But it can also be run to improve the readability of the qlog file. To do so, use the following command:

```
python3 src/qlog_parser.py IN -o OUT
```

where IN is the path to a qlog_file, and OUT is the name of the new, more readable file.

You can also get general informations about a transmission by using the `-d` flag, or print the list of fields using `--list-fields`.

More details can be found by using the `-h` flag.

#### [Share_bandwidth.py](../src/share_bandwidth.py)

This script allows to show how the available bandwidth is divided between 2 hosts, to use it, simply use:

```
python3 src/share_bandwidth.py DIR -b MAX_BW
```

where:
- DIR is a path to a directory containing the 2 qlogs used for the plot
- MAX_BW is the maximum bw used for the transmission, in Mbps

#### [Plot_rtt_rate.py](../src/plot_rtt_rate.py)

This script allows to show how a cca is using the bandwidth, as well as the rtt. You could see thus what a cca favors in term of latency/bandwidth.

```
python3 src/plot_rtt_rate.py DIR
```

where:
- DIR is a path to a directory containing the 2 qlogs to compare

### Modifying the constants for the congestion controllers

If you want to modify variables of the congestion controller to see the effects it may have on the transmission, you can do it quite simply. Per example, to modify the MAX_DATAGRAM_SIZE (=MSS in TCP), you can do the following:

```
import aioquic.quic.congestion as congestion

congestion.K_MAX_DATAGRAM_SIZE = NEW_VALUE
```

This hold for any variable you want to modify in the client.py, just import the good module.

### Playing with the network configuration to emulate losses/limitations

Below we will present a list of commands to simulate losses/limitations of the network. You can paste them on the emulated devices (router1), although they also work on a real device. Be careful that on the emulated devices, you will already be in root mode, so **don't** put the sudo command.

#### Modify the rate of error with netem

```
sudo tc qdisc add dev lo root netem loss 25%
```

Running this command will make a loss of 25% of the packets on the loopback interface 

#### Modify delay

```
sudo tc qdisc add dev lo root netem delay 100ms
```

Running this command will make a delay of 100ms on the loopback interface 

#### Limiting the bandwidth using TBF

```
sudo tc qdisc add dev eth2 root tbf rate 256kbit burst 1600 limit 3000
```

By running this (not so) simple command, you will limit the bandwidth on your eth2 interface to a maximum of 256kbps

#### Deleting a previous modification

```
sudo tc qdisc del dev eth0 root
```

This command will delete the previous modifications you applied to an interface

#### Comprehensive explanations to go further

The commands seen above are just the basics we use currently in the lab. To go further, you can check [this ressource](https://www.cs.unm.edu/~crandall/netsfall13/TCtutorial.pdf), which present another set of commands if you want to test even more configurations.

## Troubleshooting

### SSH instabilities

Some people experienced unstability while running ssh. If you encouter this problem, first we're sorry for you, and second, here's a possible work-around to still connect to the devices.

- One way of doing it is using kathara:

    ```
    kathara connect DEV_NAME -d lab
    ```

- Another way of doing it is by using directly docker:

    First, get the docker device name using by replacing DEV_NAME
    ```
    docker ps | grep DEV_NAME
    ```
    Then, you can connect to the device using 
    ```
    docker exec -it MAIN_CONTAINER_NAME /bin/bash 
    ```