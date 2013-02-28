# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

import colorsys
from pandas.io.data import *
import pylab
import random as rn
import numpy as np

# Dow Jones companies
companies = ['MMM', 'AA', 'AXP', 'T', 'BAC',
             'BA', 'CAT', 'CVX', 'CSCO', 'DD',
             'XOM', 'GE', 'HPQ', 'HD', 'INTC',
             'IBM', 'JNJ', 'JPM', 'MDC', 'MRK',
             'MSFT', 'PFE', 'PG', 'KO', 'TRV',
             'UTX', 'VZ', 'WMT', 'DIS', 'KFT']

## Download the data
data = dict()
for i in companies:
    raw_data = DataReader(i, 'yahoo', start='01/01/2009', end='23/09/2012')
    data[i] = raw_data['Close']  # we need closing prices only

## A quick visualization
colors = 'bcgmry'
rn.seed = len(companies)  # for choosing random colors
pylab.subplot('111')  # all time series on a single figure

for i in companies:
    data[i].plot(style=colors[rn.randint(0, len(colors) - 1)])
pylab.show()

## Compute correlation matrix
n = len(companies)
corr_matrix = np.zeros((n, n))

for i in range(0, n):
    for j in range(0, n):
        if i < j:
            corr_matrix[i][j] = data[companies[i]].corr(data[companies[j]], method='pearson')

# Output
np.set_printoptions(precision=2)
print corr_matrix[0]

## Remove weak correlations to construct a graph
threshold = 0.7
corr_matrix[np.where(abs(corr_matrix) < threshold)] = 0

# Output
print corr_matrix[0]

# Constructing a graph
import networkx as nx
G = nx.Graph(corr_matrix)

# Connected components: color them differently
rn.seed = 5  # for choosing random colors
components = nx.connected_components(G)

for i in components:
    component = G.subgraph(i)
    nx.draw_graphviz(component,
        node_color = colors[rn.randint(0, len(colors) - 1)],
        node_size = [component.degree(i) * 100 + 15
                     for i in component.nodes()],
        edge_color = [corr_matrix[i][j] * 0.5
                      for (i, j) in component.edges()],
        with_labels = True,
        labels = dict([(x, companies[x]) for x in component.nodes()])
        )
pylab.show()

print "Smallest components (size < 5):"
for i in components:
    if len(i) < 5:
        print [companies[j] for j in i]

print "Companies with degrees < 5:"
print [(companies[i], degrees[i]) for i in range(0, n) if degrees[i] < 5]

## Explore graph properties
nodes, edges = G.order(), G.size()
print "Number of nodes:", nodes
print "Number of edges:", edges
print "Average degree:", edges / float(nodes)

## Count degrees
degrees = G.degree()
values = sorted(set(degrees.values()))
counts = [degrees.values().count(x) for x in values]

# Generate colors -
# http://stackoverflow.com/questions/876853/generating-
# color-ranges-in-python
ncolors = len(values)
HSV_tuples = [(x * 1.0 / ncolors, 0.5, 0.5) for x in range(ncolors)]
RGB_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)

# Plot degree distribution
pylab.xlabel('Degree')
pylab.ylabel('Number of nodes')
pylab.title('Dow Jones network: degree distribution')
pylab.bar(values, counts, color=RGB_tuples)
pylab.show()

print "Highest degree:", max(values)
