# Author : Doeraene Anthony

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import argparse
import os
from qlog_parser import open_qlog, generate_rtt_bw_dataframe, filter_event

def plot_share_bandwidth(dataframe):

    sns.kdeplot(data=dataframe, x=F"rtt", y=F"delivery_rate", hue="name") 
 
    plt.ylim((0, max(df["delivery_rate"]) * 1.1))

    plt.title("Bandwidth and rtt for different cca")


parser = argparse.ArgumentParser()

parser.add_argument('dir', help="Path to a dir containing the qlogs")

args = parser.parse_args()

files = []
for file in os.listdir(args.dir):
    files.append(os.path.join(args.dir, file))

qlogs = []
for file in files:
    qlog = open_qlog(file)

    qlog = filter_event(qlog, ["recovery:metrics_updated"])

    qlogs.append(qlog)

df = generate_rtt_bw_dataframe(qlogs)

plot_share_bandwidth(df)

plt.show()