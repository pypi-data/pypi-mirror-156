#  This file is part of the Traffic Assignment Package developed at KU Leuven.
#  Copyright (c) 2020 Paul Ortmann
#  License: GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007, see license.txt
#  More information at: https://gitlab.mech.kuleuven.be/ITSCreaLab
#  or contact: ITScrealab@kuleuven.be
#
#
#
#
#
from dyntapy import get_toy_network
import numpy as np
from dyntapy.visualization import show_network, show_dynamic_network, show_demand
from dyntapy.supply_data import relabel_graph
from dyntapy.demand import DynamicDemand
from dyntapy.demand_data import od_graph_from_matrix, add_centroids
from dyntapy.demand import SimulationTime
from dyntapy.assignments import DynamicAssignment

toy_network = 'simple_bottleneck'
g = get_toy_network(toy_network)
centroid_x = np.array([0, 7])
centroid_y = np.array([0.9, 0.9])
g = add_centroids(g, centroid_x, centroid_y,
                  euclidean=True)  # also adds connectors automatically
g = relabel_graph(g)  # adding link and node ids, connectors and centroids
# are the first elements
show_network(g, toy_network=True, title=toy_network)
od_matrix = np.zeros(4).reshape((2, 2))
# value to trigger bottleneck : 131.98
#
od_matrix[0, 1] = 134
od_graph = od_graph_from_matrix(od_matrix, centroid_x, centroid_y)
show_demand(od_graph, toy_network=True)
dynamic_demand = DynamicDemand([od_graph], insertion_times=[0])
# convert everything to internal representations and parse
simulation_time = SimulationTime(np.float32(0.0), np.float32(2.0), step_size=0.25)
assignment = DynamicAssignment(g, dynamic_demand, simulation_time)
flows, costs = assignment.run()
show_dynamic_network(g, simulation_time, toy_network=True,
                     link_kwargs={'flows': flows, 'costs': costs},
                     title='assignment on ' + toy_network)
