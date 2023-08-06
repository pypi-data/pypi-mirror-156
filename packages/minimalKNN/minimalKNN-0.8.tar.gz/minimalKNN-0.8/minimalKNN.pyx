#!/usr/bin/env cython
# -*- coding: utf-8 -*-
from libcpp.vector cimport vector as vec
from libcpp.set cimport set as cset
from libcpp.list cimport list as clist
from numpy cimport ndarray
import numpy as np
import sys


cdef extern from 'minimalKNN.h' namespace 'minimalKNN':

  ## a three-dimensional vertex.
  ctypedef struct vertex:
    double x
    double y
    double z
  ## a list of three-dimensional vertices.
  ctypedef vec[vertex] vertices

  ## a unique sequential number of a vertex.
  ctypedef long node_t
  ## a list of node numbers.
  ctypedef vec[node_t] node_list

  ## a edge specified by a pair of node numbers.
  ctypedef struct edge:
    node_t u
    node_t v
  ## a unique set of edges.
  ctypedef cset[edge] graph

  ## k-NN container
  cdef cppclass kNNSet:
    kNNSet()
    kNNSet(const int)
    const kNNSet operator=(const kNNSet)
    const node_list neighbors() const

  ctypedef vec[kNNSet] kNNGraph

  ## k-NN builder
  cdef cppclass kNNBuilder:
    kNNBuilder(const vertices, const int)
    const void print_vertices() const
    const void print_nng(const int) const
    const vertices get_vertices() const
    const graph compressed_graph(const int) const
    const kNNGraph neighbor_graph() const
    const kNNGraph reversed_graph() const


cdef extern from *:
  pass


def generate_graph(
    ndarray pool, int graph_size = 10):
  ''' Construct k-Nearest Neighbor Graph.

  Construct an approximated k-Nearest Neighbor of the given set of points in
  a 3D Euclidean space using the NN-descent algorithm. The points are given
  by `pool`, which should be a `numpy.ndarray` object with the shape of
  (N, 3), where N is the number of the points. `graph_size` is an internal
  parameter in constructing the k-NN graph, which controls the size of node
  containers in _kNNBuilder_. When `graph_size` is too small, the NN-descent
  will fail. The default value of `graph_size` is, tentatively, set to 10.

  Parameters:
    pool (ndarray): (N,3) array, a list of vertices in a 3D Euclidean space.
    graph_size (int): the size of in `kNNBuilder`.

  Return:
    Bk (list): a k-Nearest Neighbor Graph.
    Rk (list): a reversed k-Nearest Neighbor Graph.
  '''
  cdef vertices V
  for v in pool:
    V.push_back(vertex(v[0], v[1], v[2]))
  cdef kNNBuilder* pkNN = new kNNBuilder(V, graph_size)
  Bk,Rk = list(),list()
  cdef kNNGraph g = pkNN.neighbor_graph()
  cdef int i = 0, s = g.size()
  for i in range(s):
    Bk.append(list(g[i].neighbors()))
  cdef kNNGraph h = pkNN.reversed_graph()
  cdef int j = 0, t = g.size()
  for j in range(t):
    Rk.append(list(h[j].neighbors()))
  return Bk,Rk


def compressed_graph(
    ndarray pool, int n_neighbor, int graph_size = 10):
  ''' Construct a compressed form of a k-Nearest Neighbor Graph.

  Construct an approximated k-Nearest Neighbor of the given set of points in
  a 3D Euclidean space using the NN-descent algorithm. The points are given
  by `pool`, which should be a `numpy.ndarray` object with the shape of
  (N, 3), where N is the number of the points. The number of edges per vertex
  is specified by `n_neighbor`. `graph_size` is an internal parameter in
  constructing the k-NN graph, which controls the size of node containers
  in _kNNBuilder_. When `graph_size` is too small, the NN-descent will fail.
  The default value of `graph_size` is, tentatively, set to 10.

  Parameters:
    pool (ndarray): (N,3) array, a list of vertices in a 3D Euclidean space.
    n_neighbor (int): the number of elements composing a line segment.
    graph_size (int): the size of in `kNNBuilder`.

  Return:
    A list of the edges of the k-Nearest Neighbor Graph.
  '''
  cdef vertices V
  for v in pool:
    V.push_back(vertex(v[0], v[1], v[2]))
  cdef kNNBuilder* pkNN = new kNNBuilder(V, graph_size)
  cdef graph g = pkNN.compressed_graph(n_neighbor)
  return [(e.u,e.v) for e in g]


def simple_demo_box(
    int n_size=50, int n_neighbor=1, int graph_size=10, int seed=42):
  ''' Demo with vertices randomly distributed in a box.

  Randomly put `vertex` elements in a (-1,1) x (-1,1) space. Construct
  an approximated k-Nearest Neighbor Graph using NN-descent algorithm
  with the Euclidean metric. The number of vertices is given by `n_size`.
  The number of edges per vertex is given by `n_neighbor`. `graph_size`
  is an internal parameter in constructing the k-NN graph, which controls
  the size of node containers in _kNNBuilder_.

  This demo function displays the generated vertices and the edges of the
  constructed k-NN graph. They are dumped in the standard output. The result
  is visualized in a Matplotlib window. The elapsed time for constructing
  the k-NN graph is given in milliseconds.

  Parameters:
    n_size (int): the number of randomly generated vertices.
    n_neighbor (int): the number of elements composing a line segment.
    graph_size (int): the size of in `kNNBuilder`.
  '''
  from datetime import datetime
  t0 = datetime.now()
  cdef vertices V
  np.random.seed(seed)
  obj = np.random.uniform(-1,1,size=(n_size,2))
  for v in obj: V.push_back(vertex(v[0], v[1], 0.0))
  cdef kNNBuilder* pkNN = new kNNBuilder(V, graph_size)
  cdef graph g = pkNN.compressed_graph(n_neighbor)
  t1 = datetime.now()

  pkNN.print_vertices()
  print('\n')
  pkNN.print_nng(n_neighbor)

  dprint = lambda s: print(s, file=sys.stderr)
  dprint('# found {} segments'.format(g.size()))
  dprint('# elapsed time: {}ms'.format((t1-t0).total_seconds()*1e3))

  import matplotlib.pyplot as plt
  from matplotlib.collections import LineCollection as lc
  fig = plt.figure(figsize=(8,8))
  ax  = fig.add_subplot(111)
  ax.scatter(obj[:,0],obj[:,1])
  edges = lc([(obj[e.u,:2],obj[e.v,:2]) for e in g], color=(1,0,0,0.5))
  ax.add_collection(edges)
  fig.tight_layout()
  plt.show()


def simple_demo_box3d(
    int n_size=200, int n_neighbor=1, int graph_size=10, int seed=42):
  ''' Demo with vertices randomly distributed in a box.

  Randomly put `vertex` elements in a (-1,1) x (-1,1) x (-1,1) space.
  Construct an approximated k-Nearest Neighbor Graph using NN-descent
  algorithm with the Euclidean metric. The number of vertices is given
  by `n_size`. The number of edges per vertex is given by `n_neighbor`.
  `graph_size` is an internal parameter in constructing the k-NN graph,
  which controls the size of node containers in _kNNBuilder_.

  This demo function displays the generated vertices and the edges of the
  constructed k-NN graph. They are dumped in the standard output. The result
  is visualized in a Matplotlib window. The elapsed time for constructing
  the k-NN graph is given in milliseconds.

  Parameters:
    n_size (int): the number of randomly generated vertices.
    n_neighbor (int): the number of elements composing a line segment.
    graph_size (int): the size of in `kNNBuilder`.
  '''
  from datetime import datetime
  t0 = datetime.now()
  cdef vertices V
  np.random.seed(seed)
  obj = np.random.uniform(-1,1,size=(n_size,3))
  for v in obj: V.push_back(vertex(v[0], v[1], v[2]))
  cdef kNNBuilder* pkNN = new kNNBuilder(V, graph_size)
  cdef graph g = pkNN.compressed_graph(n_neighbor)
  t1 = datetime.now()

  pkNN.print_vertices()
  print('\n')
  pkNN.print_nng(n_neighbor)

  dprint = lambda s: print(s, file=sys.stderr)
  dprint('# found {} segments'.format(g.size()))
  dprint('# elapsed time: {}ms'.format((t1-t0).total_seconds()*1e3))

  import matplotlib.pyplot as plt
  from mpl_toolkits.mplot3d import Axes3D
  from mpl_toolkits.mplot3d.art3d import Line3DCollection as lc
  fig = plt.figure(figsize=(8,8))
  ax  = fig.add_subplot(111, projection='3d')
  ax.scatter(obj[:,0],obj[:,1],obj[:,2])
  edges = lc([(obj[e.u,:],obj[e.v,:]) for e in g], color=(1,0,0,0.5))
  ax.add_collection(edges)
  fig.tight_layout()
  plt.show()
