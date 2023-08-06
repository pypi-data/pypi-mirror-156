import numpy as np
import pandas as pd
import os
import pydot
# from rpi_d3m_primitives_part2.pycausal.pycausal import pycausal as pc 
# from rpi_d3m_primitives_part2.pycausal import search as s
from pycausal.pycausal import pycausal as pc 
from pycausal import search as s
import sys
import scipy.io as sio 
from rpi_d3m_primitives_part2.pyBN.classes.bayesnet import BayesNet
import graphviz
from graphviz import Digraph

def draw_graph(DAG, names) -> None:
    nodes = []
    N = DAG.shape[0]
    g = Digraph(format = 'png')
    for parent in range(N):
        for child in range(N):
            if DAG[parent][child] == 1:
                if parent not in nodes:
                    nodes.append(names[parent])
                    g.node(names[parent])
                if child not in nodes:
                    nodes.append(names[child])
                    g.node(names[child])
                g.edge(names[parent], names[child])
    return g

def Edges_to_DAG_BN(V, E, D) -> np.ndarray:
	# N = len(V)
	dag = np.zeros((D, D))
	for e in E:
		parent, child = e.split(' --> ')
		dag[int(parent), int(child)] = 1
	return dag

def BayesNetToDag(BayesNet) -> np.ndarray:
	# input: BayesNet is a BayesNet object of pyBN package
	# Output: a matrix shows the relationship of Nodes
	DAG = np.zeros((len(BayesNet.E), len(BayesNet.E)))
	for N in BayesNet.V:
		for v in BayesNet.E[N]:
			DAG[N,v] = 1
	return DAG