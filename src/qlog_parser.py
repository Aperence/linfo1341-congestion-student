# Author : Doeraene Anthony

import json
import argparse
import os
import secrets
from copy import copy
import numpy as np
import pandas as pd

def open_qlog(filename):
    with open(filename, "r") as file:
        loaded = json.loads(file.read())
        return loaded
    
def event_in_list(event, events_list):
    for e in events_list:
        src, action = event.split(":")  # get the component that generated the event as well as the actual action
        e = e.split(":")
        if (len(e) == 1 and src == e[0]):  # check if it comes from same source only
            return True
        else:       # filter on action too
            if (e[0] == src and e[1] == action): return True
    return False
    
def filter_event(qlogs, events_names):
    new_qlogs = copy(qlogs)
    new_qlogs["traces"] = []
    for trace in qlogs["traces"]:

        new_trace = copy(trace)
        new_trace["events"] = list(filter(lambda event: event_in_list(event["name"], events_names), trace["events"]))
        new_qlogs["traces"].append(new_trace)

    return new_qlogs

def zip_delivery_rates(qlog1, qlog2, name1="A", name2="B"):
    qlog1 = filter_event(qlog1, ["recovery:metrics_updated"])
    qlog2 = filter_event(qlog2, ["recovery:metrics_updated"])

    events1 = qlog1["traces"][0]["events"]
    events2 = qlog2["traces"][0]["events"]

    

    times = {}
    for j, events in enumerate([events1, events2]):
        for event in events:
            if event["data"]["Phase"] == "slow-start": 
                # don't plot for slow-start, isn't stable in this phase
                continue
            rounded = round(event["time"] / 10) * 10 # round at 10ms close
            if not rounded in times:
                times[rounded] = ([], [])
            times[rounded][j].append(8 * event["data"]["delivery_rate"] / 1e6)  # convert in Mbps
  
    ret = np.zeros((len(times), 2), dtype=np.float64)
    i = 0
    for _, value in times.items():
        (delivery_rate1, delivery_rate2) = value
        ret[i, 0] = np.mean(delivery_rate1) if len(delivery_rate1) != 0 else 0
        ret[i, 1] = np.mean(delivery_rate2) if len(delivery_rate2) != 0 else 0
        i+=1

    return pd.DataFrame({F"Bandwidth used by {name1} [Mbps]" : ret[:, 0], F"Bandwidth used by {name2} [Mbps]" : ret[:, 1]})

def generate_rtt_bw_dataframe(qlogs):

    df = pd.DataFrame()

    for qlog in qlogs:
        rtts = []
        bws = []

        rtt = 0

        for event in qlog["traces"][0]["events"]:
            if event["data"]["Phase"] == "slow-start": 
                continue
            if "latest_rtt" in event["data"]:
                rtt = event["data"]["latest_rtt"]
            rtts.append(rtt)
            bws.append(8 * event["data"]["delivery_rate"] / 1e6)

        assert len(bws) == len(rtts)
        names = [get_name(qlog) for _ in range(len(rtts))]
        new_df = pd.DataFrame({"rtt" : rtts, "delivery_rate" : bws, "name" : names})
        df = pd.concat([df, new_df])

    return df


def get_fields(qlog):
    fields = set()

    for event in qlog["traces"][0]["events"]:
        for field in event["data"]:
            fields.add(field)
    
    return list(fields)

def add_name(qlogs, name):
    qlogs["name_client"] = name

def get_name(qlogs):
    return qlogs.get("name_client", None)

def write_qlogs(qlogs, dir):
    path = os.path.join(dir, secrets.token_hex(8) + ".qlog")
    with open(path, "w") as file:
        file.write(json.dumps(qlogs))

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('filename')
    parser.add_argument("-o", '--out', default="out", help="Filename where the beautified version of json should be written")
    parser.add_argument("-d", '--details', action="store_true", help="Print details about the transmission")
    parser.add_argument("-l", '--list-fields', action="store_true", help="Print the field contained in the qlog fielfd, which can be plotted")

    args = parser.parse_args()

    qlogs = open_qlog(args.filename)

    qlogs = filter_event(qlogs, ["recovery"])

    if (args.list_fields):
        print(F"List of fields : \n{get_fields(qlogs)}")

    if (args.details):

        losses = filter_event(qlogs, ["recovery:packet_lost"])

        nb_lost = len(losses["traces"][0]["events"]) 

        #lost_bytes = 

        nb_packets = len(qlogs["traces"][0]["events"])

        ratio = nb_lost / nb_packets 

        print(F"Name of scenario : {get_name(qlogs)}\nTotal number of packets exchanged : {nb_packets}\nTotal number of losses : {nb_lost}\nLoss ratio : {ratio*100:.3f}%")
        exit(0)

    with open(args.out, "w") as file:
        file.write(json.dumps(qlogs, indent=4))
