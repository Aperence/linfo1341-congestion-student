# Author : Doeraene Anthony

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import argparse
from qlog_parser import open_qlog, zip_delivery_rates, get_name
import os

def plot_share_bandwidth(pairs, max_bw, name1="A", name2="B"):

    # plot the border of the box
    plt.hlines(y=0, xmin=0, xmax=max_bw, colors='g', ls='--', lw=2)
    plt.hlines(y=max_bw, xmin=0, xmax=max_bw, colors='b', ls='--', lw=2)
    plt.vlines(x=0, ymin=0, ymax=max_bw, colors='g', ls='--', lw=2)
    plt.vlines(x=max_bw, ymin=0, ymax=max_bw, colors='b', ls='--', lw=2)
    
    n = 100
    sample = np.linspace(0, max_bw, n)
    plt.plot(sample, sample, ls="--", color="r", label="Fair distribution")
    plt.plot(sample, sample[::-1], ls="--", color="g", label="Congestion limit")

    sns.kdeplot(data=pairs, x=F"Bandwidth used by {name1} [Mbps]", y=F"Bandwidth used by {name2} [Mbps]", fill=True) 
 
    plt.legend(loc='upper right', fancybox=True, shadow=True)
    
    plt.ylim(0, max_bw*1.2)
    plt.xlim(0, max_bw*1.2)

    plt.title("Repartition of delivery rate between 2 hosts")


parser = argparse.ArgumentParser()

parser.add_argument('dir', help="Path to a dir containing 2 qlog files")
parser.add_argument("-b", '--max_bw', type=int, default=8, help="The bottleneck bandwidth used during a transmission")


args = parser.parse_args()

files = []
for file in os.listdir(args.dir):
    files.append(os.path.join(args.dir, file))


qlogs1, qlogs2 = open_qlog(files[0]), open_qlog(files[1])
name1 = get_name(qlogs1); name2 = get_name(qlogs2)
if name1 == None or name1 == "": name1 = "A"
if name2 == None or name2 == "": name2 = "B"

if name1 == name2:
    name1 += "1"
    name2 += "2"

samples = zip_delivery_rates(qlogs1, qlogs2, name1, name2)

plt.figure(figsize=(8, 8))

plot_share_bandwidth(samples, args.max_bw, name1, name2)

plt.show()
