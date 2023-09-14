#!/usr/bin/python3

# Author : Doeraene Anthony

import argparse

def parse_ip(str):
    return tuple(map(lambda sub : int(sub), str.split(".")))

def str_ip(ip):
    return ".".join(map(lambda sub : str(sub), ip))

router1_W = parse_ip("10.0.0.3")
router1_E = parse_ip("10.0.2.1")
router2_W = parse_ip("10.0.2.2")
router2_E = parse_ip("10.0.1.3")

dns = {
    "client1" : "10.0.0.1",
    "client2" : "10.0.0.2",
    "server1" : "10.0.1.1",
    "server2" : "10.0.1.2"
}

def get_expected_route(src, dest):
    if src == dest: return [dest]
    if src[2] == dest[2]:
        # in the same subdomain, just connect directly to dest
        return [dest]
    # different subdomain, check if we need to go from clients to servers of from servers to clients
    if src[2] == 0:
        # from a client to a server
        return [router1_W, router2_W, dest]
    else:
        return [router2_E, router1_E, dest]


def is_route_correct(actual, src, dest):
    expected = get_expected_route(src, dest)
    if (len(expected) != len(actual)):
        return False
    for i in range(len(expected)):
        if (expected[i] != actual[i]):
            return False
    return True

def parse_route(str):
    return list(map(
        lambda ip : 
            parse_ip(ip),
        str.split("\n")
    ))

def str_route(route):
    str = ""
    for i, ip in enumerate(route):
        str += str_ip(ip)
        if i != len(route) - 1:
            str += "\n"
        
    return str

parser = argparse.ArgumentParser(
                    prog='Check route',
                    description='Check if a route is correct')

parser.add_argument('route')           # positional argument
parser.add_argument('-s', '--src')      # option that takes a value
parser.add_argument('-d', '--dest')

args = parser.parse_args()

src = args.src
dest = args.dest

# get the real ip, and convert ip to a tuple of 4 elements
args.src = dns[args.src]
args.src = parse_ip(args.src)

# convert ip to a tuple of 4 elements
args.dest = parse_ip(args.dest)

route = parse_route(args.route)
if is_route_correct(route, args.src, args.dest):
    exit(0)
else:
    print(F"Error for {src} to {dest}\nExpected route : \n{str_route(get_expected_route(args.src, args.dest))}\nGot : \n{args.route}")
    exit(1)