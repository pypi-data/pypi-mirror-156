/**
 * @file minimalKNN.h
 * @brief header fiel for the MinimalKNN library
 * @author Ryou Ohsawa
 * @year 2020
 */
#ifndef __MINIMALKNN_H_INCLUDE
#define __MINIMALKNN_H_INCLUDE

#include <functional>
#include <algorithm>
#include <utility>
#include <limits>
#include <vector>
#include <random>
#include <set>


namespace minimalKNN {
  constexpr bool __debug__ = false;

  /** a container to store k-Nearest Neigbors. */
  class kNNSet;
  /** a constructor of k-Nearest Neighbor Graph. */
  class kNNBuilder;

  /** a vertex in a three-dimensional space. */
  typedef struct vertex {
    double x;
    double y;
    double z;
  } vertex;
  /** a list of three-dimensional vertices. */
  typedef std::vector<vertex> vertices;

  /** a distance between two vertices. */
  typedef double distance_t;

  /** a unique sequential number of a vertex. */
  typedef long node_t;
  /** a list of node numbers.  */
  typedef std::vector<node_t> node_list;
  /** a node with the distance. */
  typedef struct rated_node {
    node_t i;
    distance_t distance;
    const bool operator<(const rated_node& rhs) const
    { return distance < rhs.distance; }
    const bool operator==(const node_t& rhs) const
    { return i == rhs; }
    const bool operator==(const rated_node& rhs) const
    { return i == rhs.i; }
  } rated_node;

  /** a pair of vertices specified by node numbers. */
  typedef struct edge {
    node_t u;
    node_t v;
    const bool operator<(const edge& rhs) const
    { return (u==rhs.u)?v<rhs.v:u<rhs.u; }
  } edge;
  /** a list of edges. */
  typedef std::vector<edge> edges;
  /** a unique set of edges. */
  typedef std::set<edge> graph;

  /** a container of a k-Nearest Neighbor Graph. */
  typedef std::vector<kNNSet> kNNGraph;

  /** a function to calculate the distance between vertices */
  typedef std::function<distance_t(const vertex&,const vertex&)> metric;

  /**
   * @brief calculate the squared Euclidean distance between two vertices.
   * @param[in] v: the first vertex.
   * @param[in] w: the second vertex.
   * @return the squared Euclidean distance between two vertices.
   */
  const distance_t
  sq_euclidean_dist(const vertex& v, const vertex& w)
  {
    return std::pow(v.x-w.x,2)+std::pow(v.y-w.y,2)+std::pow(v.z-w.z,2);
  }

  /**
   * @brief calculate the manhattan distance between two vertices.
   * @param[in] v: the first vertex.
   * @param[in] w: the second vertex.
   * @return the manhattan distance between two vertices.
   */
  const distance_t
  manhattan_dist(const vertex& v, const vertex& w)
  {
    return std::abs(v.x-w.x)+std::abs(v.y-w.y)+std::abs(v.z-w.z);
  }

  class kNNSet {
  public:
    /**
     * @brief construct a _kNNSet_ without the size limitation.
     */
    kNNSet()
      : kNNSet(std::numeric_limits<long>::max())
    {}

    /**
     * @brief construct a _kNNSet_ with graph size of `k`.
     * @param[in] k: the storage size of the internal graph.
     */
    kNNSet(const size_t k)
      : graph_size(k),
        max_distance(std::numeric_limits<double>::max())
    {}

    /**
     * @brief a copy constructor of _kNNSet_.
     * @param[in] obj: a _kNNSet_ object to be copied.
     */
    kNNSet(const kNNSet& obj)
      : graph_size(obj.graph_size),
        max_distance(obj.max_distance), B(obj.B)
    {}

    /**
     * @brief a move constructor of _kNNSet_.
     * @param[in] obj: a temprary _kNNSet_ objet to be copied.
     */
    kNNSet(kNNSet&& obj)
      : graph_size(obj.graph_size),
        max_distance(obj.max_distance), B(std::move(obj.B))
    {}

    /**
     * @brief a substitute operator of _kNNSet_.
     * @param[in] obj: a _kNNSet_ object to be substituted.
     * @note this function is requried for the Cython interpreter.
     */
    const kNNSet&
    operator=(const kNNSet& obj)
    { return obj; }

    /**
     * @brief insert a node into a container with a distance.
     * @param[in] node: the nubmber of the node to be inserted.
     * @param[in] distance: the distance to the node to be inserted.
     * @return true if a node is successfully inserted.
     * @note When the container can accommodate a node, the node insertion
     *       is always successful. If the distance to the node is larger
     *       than the maximum distance of the stored nodes, the insertion
     *       will fail. In case that the distance is exactly zero, which
     *       means that the node is idential to that of this object, the
     *       node is not inserted.
     */
    bool
    insert(const node_t& node, const distance_t& distance)
    {
      if (distance == 0) return false;
      if (distance < max_distance || B.size() < graph_size) {
        if (B.find({node,distance})!=B.end()) return false;
        B.insert(rated_node{node, distance});
        if (B.size() > graph_size) B.erase(prev(B.end()));
        max_distance = prev(B.end())->distance;
        return true;
      }
      else {
        return false;
      }
    }

    /**
     * @brief display the associated nodes and their distances.
     */
    void
    print() const
    {
      for (const auto& e: B)
        printf("[%2ld (%.2f)]", e.i, e.distance);
      printf("\n");
    }

    /**
     * @brief inquire for the node by the node number.
     * @param[in] node: the node number.
     * @return a forward iterator of the _kNNSet_ container.
     * @note kNNSet.end() is returned if the requested node is absent.
     */
    const std::set<rated_node>::const_iterator
    find(const node_t& node) const
    {
      return B.find(rated_node{node, 0.0});
    }

    /**
     * @brief an iterator to the beginning.
     * @return an iterator to the beginning of the container.
     */
    std::set<rated_node>::iterator
    begin() const
    {
      return B.begin();
    }

    /**
     * @brief an iterator to the end.
     * @return an iterator to the end of the container.
     */
    std::set<rated_node>::iterator
    end() const
    {
      return B.end();
    }

    /**
     * @brief return a list of the k-Nearest Neighbor nodes.
     * @return a list of the neighbor nodes.
     */
    const node_list
    neighbors() const
    {
      node_list ret;
      for (auto& s: B) ret.push_back(s.i);
      return ret;
    }

  private:
    const size_t graph_size; /** the maximum size of the container. */
    double max_distance;     /** an auxiliary maximum-distance variable. */
    std::set<rated_node> B;  /** an internal container of nodes. */
  };


  /** a default value for the maximum size of the node containsers. */
  constexpr size_t default_kNN_graph_size = 10;
  /** the maximum number of iterations in the optimization. */
  constexpr size_t kNN_max_iter = 15;

  class kNNBuilder {
  public:
    /**
     * @brief construct a _kNNBuilder_ with `default_kNN_graph_size`.
     * @param[in] v: a list of the given vertices.
     */
    kNNBuilder(const vertices v) : kNNBuilder(v, default_kNN_graph_size)
    {}

    /**
     * @brief construct a _kNNBuilder_.
     * @param[in] v: a list of the given vertices.
     * @param[in] k: the maximum size of the node containers.
     * @note The graph construction will fail when the `k` value is too small.
     *       The `k` is conventionally set between 10--20.
     */
    kNNBuilder(const vertices v, const size_t k)
      : kNNBuilder(v, k, sq_euclidean_dist)
    {}

    /**
     * @brief construct a _kNNBuilder_.
     * @param[in] v: a list of the given vertices.
     * @param[in] k: the maximum size of the node containers.
     * @param[in] m: the function to measure the distance between vertices.
     * @note The graph construction will fail when the `k` value is too small.
     *       The `k` is conventionally set between 10--20.
     */
        kNNBuilder(const vertices v, const size_t k, const metric m)
      : n_vertices(v.size()), graph_size((k<n_vertices)?k:n_vertices),
        f_metric(m), V(v)
    {
      // Initialization Procedure
      //   The k-NN graph is initialized with randomly selected nodes.
      //   `std::shuffle` should be replaced with a more efficient algorithm.
      std::mt19937 gen;
      gen.seed(std::random_device{}());
      node_list r(n_vertices);
      std::iota(r.begin(), r.end(), 0);
      for (size_t i=0; i<n_vertices; i++) {
        kNNSet b(graph_size);
        std::shuffle(r.begin(), r.end(), gen);
        for (size_t j=0; j<graph_size; j++)
          b.insert(r[j], calc_distance(i,r[j]));
        Bk.push_back(b);
      }

      // Optimization Loop
      //   kNNBuilder will give up the optimization procedure after the
      //   `kNN_max_iter` iterations. Currently, no exception is raised.
      //   The k-NN graph remains at the last iteration. In usual cases,
      //   the k-NN graph will converge within a few iterations.
      size_t updated(0);
      for (size_t c=0; c<kNN_max_iter; c++) {
        kNNGraph Rk = reversed_graph();
        kNNGraph Mk = merge(Bk, Rk);
        for (size_t i=0; i<n_vertices; i++) {
          for (auto& v: Mk[i]) {
            for (auto& u: Mk[v.i]) {
              distance_t&& d = calc_distance(i, u.i);
              updated += Bk[i].insert(u.i, d);
            }
          }
        }
        if (__debug__)
          printf("# %ld updates in iteration %ld.\n", updated, c);
        if (updated==0) break; // leave the loop when converged.
        updated = 0;
      }
    }


    /**
     * @brief return a list of the imported vertices.
     * @return a list ov the vertices.
     */
    const vertices
    get_vertices() const
    {
      return V;
    }

    /**
     * @brief display the vertices.
     */
    const void
    print_vertices() const
    {
      for (size_t i=0; i<n_vertices; i++)
        printf("%8.4f %8.4f %8.4f\n", V[i].x, V[i].y, V[i].z);
    }


    /**
     * @brief construct the k-Nearest Neighbor Graph.
     * @return A graph contains the k-Narest Neighbor Graph.
     * @note This displays a compressed representation of the k-NN graph.
     *       Each line corresponds to an edge (x1,y1,z1,x2,y2,z2).
     *       The graph is non-directional. Every vertex should be connected
     *       with `graph_size` edges.
     */
    const graph
    compressed_graph() const
    { return compressed_graph(graph_size); }

    /**
     * @brief construct the k-Nearest Neighbor Graph.
     * @param[in] n_neibors: the number of edges per vertex.
     * @return A graph contains the k-Narest Neighbor Graph.
     * @note This displays a compressed representation of the k-NN graph.
     *       Each line corresponds to an edge (x1,y1,z1,x2,y2,z2).
     *       The graph is non-directional. Every vertex should be connected
     *       with `n_neibors` edges.
     */
    const graph
    compressed_graph(const size_t n_neibors) const
    {
      graph G;
      for (size_t i=0; i<n_vertices; i++) {
        size_t N = 0;
        for (auto& node: Bk[i]) {
          node_t u = ((node_t)i<node.i)?i:node.i;
          node_t v = ((node_t)i<node.i)?node.i:i;
          G.insert({u, v});
          N++;
          if (N==n_neibors) break;
        }
      }
      return G;
    }

    /**
     * @brief display the k-Nearest Neighbor Graph in a compressed form.
     * @note This displays a compressed representation of the k-NN graph.
     *       Each line corresponds to an edge (x1,y1,z1,x2,y2,z2).
     *       The graph is non-directional. Every vertex should be connected
     *       with `graph_size` edges.
     */
    const void
    print_nng() const
    { print_nng(graph_size); }

    /**
     * @brief display the k-Nearest Neighbor Graph in a compressed form.
     * @param[in] n_neibors: the number of edges per vertex.
     * @note This displays a compressed representation of the k-NN graph.
     *       Each line corresponds to an edge (x1,y1,z1,x2,y2,z2).
     *       The graph is non-directional. Every vertex should be connected
     *       with `n_neibors` edges.
     */
    const void
    print_nng(const size_t n_neibors) const
    {
      graph G = compressed_graph(n_neibors);
      for (auto& g: G) {
        printf("%8.4f %8.4f %8.4f  ", V[g.u].x, V[g.u].y, V[g.u].z);
        printf("%8.4f %8.4f %8.4f\n", V[g.v].x, V[g.v].y, V[g.v].z);
      }
      if (__debug__)
        printf("# graph size: %ld\n", G.size());
    }


    /**
     * @brief return a k-Nearest Neighbor graph.
     * @return a full k-NN graph.
     */
    const kNNGraph&
    neighbor_graph() const
    {
      return Bk;
    }

    /**
     * @brief construct a reversed k-NN graph.
     * @return a reversed k-NN graph.
     * @note A k-NN graph `Gk[v]` contains the k-nearest neighbors from the
     *       vertex `v`. The reversed k-NN graph `Rk[v]` contains the nodes
     *       whose nearest neighbors contain the vertex `v`.
     */
    const kNNGraph
    reversed_graph() const
    {
      kNNGraph Rk;
      for (size_t i=0; i<n_vertices; i++)
        Rk.push_back(kNNSet());
      for (size_t i=0; i<n_vertices; i++) {
        for (auto& node: Bk[i]) {
          Rk[node.i].insert(i, node.distance);
        }
      }
      return Rk;
    }

  private:
    /**
     * @brief construct a merged k-NN graph.
     * @param[in] Fk: a k-NN graph to be merged.
     * @param[in] Gk: a k-NN graph to be merged.
     * @return a merged k-NN graph.
     * @note A merged k-NN graph `Mk[v]` contains the members of `Fk[v]` and
     *       `Gk[v]` without duplication.
     */
    const kNNGraph
    merge(const kNNGraph& Fk, const kNNGraph& Gk) const
    {
      kNNGraph Mk;
      for (size_t i=0; i<n_vertices; i++) {
        Mk.push_back(kNNSet());
        for (auto& node: Fk[i]) Mk[i].insert(node.i, node.distance);
        for (auto& node: Gk[i]) Mk[i].insert(node.i, node.distance);
      }
      return Mk;
    }

    /**
     * @brief calculate the distance between two nodes.
     * @param[in] i: the node number of the first vertex.
     * @param[in] j: the node number of the second vertex.
     * @return the distance between two nodes.
     */
    const distance_t
    calc_distance(const node_t& i, const node_t& j)
    {
      return f_metric(V[i], V[j]);
    }

    const size_t n_vertices; /** the number of the vertices. */
    const size_t graph_size; /** the maximum size of the node containers. */
    const metric f_metric;   /** the function to measure the distance. */
    vertices V;              /** the container of the vertices. */
    kNNGraph Bk;             /** the k-NN graph container. */
  };
}

#endif  // __MINIMALKNN_H_INCLUDE
