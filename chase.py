import networkx as nx
import numpy as np
import csv
from pyvis.network import Network
import pandas as pd
import sys


def main():
    
    start = int(input("Enter starting square:\n"))
    print("")
    print("Enter sequence of steps in the following format:")
    print("xxxx, where each x represents an action by Mr. X.")
    print("x can be t (taxi), b (bus), s (subway) or h ( hidden)")
    print("E.g. 'htb' -> Mr. X does a hidden action, and then moves by taxi and bus.")
    steps = input("Enter sequence:\n")
    show_graph = input("Want to see a visualization y/n?")
    
    A_t = np.zeros((199,199))
    A_b = np.zeros((199,199))
    A_s = np.zeros((199,199))
    A_f = np.zeros((199,199))


    with open('taxi.csv') as f:
        reader = csv.reader(f)
        for line in reader:
            if line[0] != "Start":
                i = int(line[0])-1
                j = int(line[1])-1
                A_t[i,j] = 1
                A_t[j,i] = 1

    with open('bus.csv') as f:
        reader = csv.reader(f)
        for line in reader:
            if line[0] != "Start":
                i = int(line[0])-1
                j = int(line[1])-1
                A_b[i,j] = 1
                A_b[j,i] = 1

    with open('subway.csv') as f:
        reader = csv.reader(f)
        for line in reader:
            if line[0] != "Start":
                i = int(line[0])-1
                j = int(line[1])-1
                A_s[i,j] = 1
                A_s[j,i] = 1
        
    with open('ferry.csv') as f:
        reader = csv.reader(f)
        for line in reader:
            if line[0] != "Start":
                i = int(line[0])-1
                j = int(line[1])-1
                A_f[i,j] = 1
                A_f[j,i] = 1

    A_h = np.where(A_t + A_b + A_s + A_f >= 1, 1, 0)
    map_steps = {"t": A_t, "b": A_b, "s":A_s, "h":A_h}

    def get_possible_nodes(start, steps):
        result = np.eye(np.shape(A_t)[0])
        for s in steps:
            result = np.dot(result,map_steps[s])
        
        return list(np.nonzero(result[start-1])[0]+1)

    def edges_to_graph(G,path,label):
        df = pd.read_csv(path)
        edge_data = zip(df.Start,df.End,[label]*df.shape[0])
        for e in edge_data:
            src = e[0]
            dst = e[1]
            w = e[2]
            G.add_node(src)
            G.add_node(dst)
            G.add_edge(src, dst, color = w, width = 2.5)
        return G

    def create_network():
        g = nx.MultiGraph()
    
        nt = Network(height='750px', width='100%', bgcolor='#222222', font_color='white')
        nt.from_nx(g)
        nt.set_edge_smooth('dynamic')
        return g

    possible_nodes = get_possible_nodes(start,list(steps))
    
    print(f"When Mr. X starts from square {start}, he can reach the following squares with the sequence {steps}:")
    print(*possible_nodes)
    if not show_graph == "y":  return True
    taxi_net = edges_to_graph(create_network(),"taxi.csv","yellow")
    taxi_bus_net = edges_to_graph(taxi_net,"bus.csv","blue")
    taxi_bus_sub_net = edges_to_graph(taxi_bus_net,"subway.csv","red")
    full_net = edges_to_graph(taxi_bus_sub_net,"ferry.csv","magenta")


    def mark_possible_nodes(net,nodes,color="lime"):
        for n in nodes:
            net.add_node(n,color=color, size=20)
        return net
    
    marked_net = mark_possible_nodes(full_net, possible_nodes)

    nt = Network(directed=True, height='750px', width='100%', bgcolor='#222222', font_color='white')
    nt.from_nx(marked_net)
    nt.set_edge_smooth('dynamic')
    nt.show("map.html")

main()
