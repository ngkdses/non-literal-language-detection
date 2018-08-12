import clusters
import pydot


def visualize_graph(nodes, edges):
    graph = pydot.Dot(graph_type='graph', mode='maxent')

    # Get minimum-spanning tree
    mst_edges, remaining_edges = clusters.kruskal(nodes, edges)

    node_dict = {}

    # Add nodes
    for word in nodes:
        node_dict[word] = pydot.Node(word)
        graph.add_node(node_dict[word])

    # Add edges
    for edge in mst_edges:
        new_edge = pydot.Edge(node_dict[edge.word_u], node_dict[edge.word_v], \
            label=int(edge.cost), len=int(edge.cost), fontcolor='red', fontsize=12, \
            color='red', style='bold')
        graph.add_edge(new_edge)
    
    for edge in remaining_edges:
        new_edge = pydot.Edge(node_dict[edge.word_u], node_dict[edge.word_v], \
            label=int(edge.cost), len=int(edge.cost), fontsize=12, style='dotted')
        graph.add_edge(new_edge)

    graph_name = ""
    for word in nodes:
        graph_name += word + '_'
    graph_name = graph_name[:-1] + ".png"

    graph.write_png(graph_name)