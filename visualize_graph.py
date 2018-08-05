import clusters
import pydot


# Minimum spanning tree
# Return list of MST edges and list of remaining edges
def kruskal(nodes, edges):
    union_find = clusters.Union_find(nodes)
    
    clusters.quicksort(edges, key=lambda edge: edge.cost)
    
    # If graph has no edges:
    if not edges:
        return None

    # Store chosen and non-chosen edges
    mst_edges = []
    remaining_edges = []

    for i in range(len(edges)):

        # Get first edge
        min_edge = edges[i]
        x, y = min_edge.word_u, min_edge.word_v

        if union_find.union(x, y):
            mst_edges.append(min_edge)
        else:
            remaining_edges.append(min_edge)

        # Once MST is complete
        if union_find.clusters == 1:
            remaining_edges += edges[i + 1:]
            break
    
    return mst_edges, remaining_edges
    

def visualize_graph(nodes, edges):
    graph = pydot.Dot(graph_type='graph', mode='maxent')

    # Get minimum-spanning tree
    mst_edges, remaining_edges = kruskal(nodes, edges)

    node_dict = {}

    # Add nodes
    for word in nodes:
        node_dict[word] = pydot.Node(word)
        graph.add_node(node_dict[word])
        # word = pydot.Node(word)

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