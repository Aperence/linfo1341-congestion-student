# Author : Doeraene Anthony

import argparse
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os
from qlog_parser import open_qlog, filter_event, get_name

K_MAX_DATAGRAM_SIZE = 1280
K_CUBIC_C = 0.4

show_wmax=False
# max number of different phases in congestion control
max_step = 4*K_MAX_DATAGRAM_SIZE
max_delay = 0.2
field = "cwnd"
show_losses = None
scatter = False
filtered_phase = None
aligned = False

colors = matplotlib.colormaps["Set1"].colors

init_time = float("inf")

def W_cubic(t, K, W_max):
    return K_CUBIC_C * (t - K)**3 + (W_max)

def better_cube_root(x):
    if x < 0 : return -((-x)**(1/3))
    else: return x**(1/3)

def plot_congestion(qlogs, fig, ax : plt.Axes):

    global init_time

    events = qlogs["traces"][0]["events"]

    phases = {}

    times = []
    cwnds = []
    losses = []
    times_W_max_reached = []
    W_max = []

    if aligned:
        init_time = events[0]["time"]

    if get_name(qlogs) != None:
        ax.set_title(get_name(qlogs))

    for event in events:

        if event["name"] == "recovery:metrics_updated":
            phase = event["data"]["Phase"] if "Phase" in event["data"] else "none"

            if not field in event["data"]:
                continue # skip this event

            if filtered_phase != None and phase.lower() != filtered_phase.lower():
                continue

            if (phase not in phases):
                phases[phase] = {"times" : [], field : []}  # a pair containing the times and field value for this phase

            t = (event["time"] - init_time)/1000    # convert in s
            phases[phase]["times"].append(t)
            if field in ["bw", "delivery_rate"]:
                phases[phase][field].append(8 * event["data"][field] / 1e6) # convert in Mbps
            else:
                phases[phase][field].append(event["data"][field])
            times.append(t)
            cwnds.append(event["data"]["cwnd"])

            if show_wmax and event["data"]["W_max"] != None:
                if len(W_max) != 0 and W_max[-1] == event["data"]["W_max"]:
                    # already added this W_max, skip
                    continue
                W_max.append(event["data"]["W_max"])
                # get the K parameter to know when W_max will be reached again
                W_max_segments = W_max[-1] / K_MAX_DATAGRAM_SIZE
                cwnd_segments = cwnds[-1] / K_MAX_DATAGRAM_SIZE
                K = better_cube_root((W_max_segments - cwnd_segments)/K_CUBIC_C)
                times_W_max_reached.append((t, t+K))

        if event["name"] == "recovery:packet_lost":
            t = (event["time"] - init_time)/1000
            losses.append(t)

    max_field = 0
    i = 0
    # if we increment only by 1, we use colors that ressemble each other
    # so, multiply it by -1 half the time to alternate between the start and end of array
    for phase in phases:
        times_temp = np.array(phases[phase]["times"], dtype=float)
        field_values = np.array(phases[phase][field], dtype=float)

        if (phase != "slow-start"):

            # break lines if the points aren't close enough
            max_l_without_inf = max(filter(lambda x : x != float("inf"), field_values))
            max_field = max(max_field, max_l_without_inf)

            pos = np.where(np.logical_or(np.abs(np.diff(field_values)) >= max_step, \
                                        np.abs(np.diff(times_temp) >= max_delay)))[0]+1
            times_temp = np.insert(times_temp, pos, np.nan)
            field_values = np.insert(field_values, pos, np.nan)

        if scatter:
            ax.scatter(times_temp, field_values , label=F"{field} ({phase})", color=colors[i], s=1)
        else:
            ax.plot(times_temp, field_values , label=F"{field} ({phase})", c=colors[i])
        i+=1 # incrementing the counter for colors



    if show_wmax:
        i = 0
        j = 0
        W_max_final = []
        W_max_times = []
        while i < len(times_W_max_reached) - 1:
            t_start, t_reached = times_W_max_reached[i]

            # get the time of start for this congestion avoidance
            while losses[j+1] < t_start:
                j += 1

            if losses[j+1] > t_reached:
                # W_max reached before another loss occurs
                W_max_final.append(W_max[i])
                W_max_times.append(t_reached)
            
            i+=1

        _, t_reach_final = times_W_max_reached[-1]
        if times[-1] > t_reach_final:
            # add if last W_max was reached before end of transmission
            W_max_final.append(W_max[-1])
            W_max_times.append(t_reach_final)
        
        ax.scatter(W_max_times, W_max_final, c="k", label="W_max reached", s=8)
        
    unit = ""
    if field in ["cwnd", "ssthresh"]:
        unit = "[B]"

    if field in ["bw", "delivery_rate"]:
        unit = "[Mbps]"

    ax.set_xlabel("Time [s]")
    ax.set_ylabel(F"{field} {unit}")

    if (max_field != 0):
        # ax.set_ylim(0, max_field*1.1)
        pass

    if show_losses:
        ax.vlines(x=losses, ymin=0, ymax=max_field*1.1, colors='darkgray', ls='--', lw=2, label='Losses')

    # put the legend outside the plot
    ax.legend(loc='lower left', bbox_to_anchor=(0, 1.02, 1, 0.2),
          ncol=3, fancybox=True, shadow=True)
    
    ax.grid()


parser = argparse.ArgumentParser(
                    prog='Congestion plotter',
                    description='Plot the results obtained in a csv')

parser.add_argument('filename', help="The name of the file containing the data to be plotted", nargs='+')
parser.add_argument("-W", '--W-max', action="store_true", default=False, help="Whether to show or not a point where W_max in cubic should be reached")  
parser.add_argument("-m", '--max-step', default=4*K_MAX_DATAGRAM_SIZE, type=int, help="The max step where lines won't be considered to be disjoint")
parser.add_argument("-d", '--max-delay', default=0.5, type=float, help="The max delay (s) where lines won't be considered to be disjoint")
parser.add_argument("-f", '--field', default="cwnd", type=str, help="The field you want to plot")
parser.add_argument("-l", "--losses", action="store_false", help="Show losses")
parser.add_argument("-s", "--scatter", action="store_true", help="Use a scatter instead of a plot")
parser.add_argument("--filter-phase", default=None, help="Which phase to plot")
parser.add_argument("-a", "--align", action="store_true", help="Align the times of transition to compare 2 graphs")
parser.add_argument("--dir", action="store_true", help="Consider the filename to be the name of a dir and plot every qlogs contained in it")

args = parser.parse_args()
show_wmax = args.W_max
max_step = args.max_step
max_delay = args.max_delay
field = args.field
show_losses = args.losses
scatter = args.scatter
filtered_phase = args.filter_phase
aligned = args.align

filenames = args.filename

if args.dir:
    filenames = list(map(lambda x : os.path.join(filenames[0], x), os.listdir(filenames[0])))

fig, axes = plt.subplots(len(filenames), 1, sharex=True, sharey=True)


# setting the size of the plot
fig.set_figwidth(19)
fig.set_figheight(7)

qlogs_list = []

for i, name in enumerate(filenames):

    # open the qlogs and retrieve data + get init_time

    qlogs = open_qlog(name)
    qlogs = filter_event(qlogs, ["recovery"])

    qlogs_list.append(qlogs)

    events = qlogs["traces"][0]["events"]

    init_time = min(init_time, events[0]["time"])


for i in range(len(qlogs_list)):
    # create a subplot for each qlog file

    ax = axes if len(filenames) == 1 else axes[i]
    plot_congestion(qlogs_list[i], fig, ax)

    print("Plotted ", filenames[i])

plt.show()