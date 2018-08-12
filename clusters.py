import math
import numpy


class Union_find:

    class UF_node:
        def __init__(self, parent, rank):
            self.id_num = parent
            self.parent = parent
            self.rank = rank

    def __init__(self, words):
        self.contents = {}
        for word in words:
            self.contents[word] = self.UF_node(word, 0)
        self.clusters = len(words)

    # Return root of node_x
    def find(self, node_x):
        compression_buffer = []

        # Traverse parent nodes until root is reached, storing traversed nodes in a buffer
        while node_x != self.contents[node_x].parent:
            compression_buffer.append(self.contents[node_x])
            node_x = self.contents[node_x].parent
        
        # Change root of all traversed nodes to the root of x
        for uf_node in compression_buffer:
            uf_node.parent = node_x
        
        return node_x

    # Union by rank
    def union(self, x, y):
        # Get roots of x and y
        s_x = self.contents[self.find(x)]
        s_y = self.contents[self.find(y)]

        # If already in same group, return False
        if s_x.parent == s_y.parent:
            return False

        elif s_x.rank > s_y.rank:
            s_y.parent = s_x.parent
        else:
            s_x.parent = s_y.parent
            if s_x.rank == s_y.rank:
                s_y.rank += 1
        self.clusters -= 1

        # If successful return True
        return True


# Sort function (increasing order, unless reverse parameter set to True)
# key parameter must be lambda function to access array item's key
def quicksort(array, key, reverse=False):

    def swap(array, index_1, index_2):
        array[index_1], array[index_2] = array[index_2], array[index_1]

    def q_routine(array, left, right):

        def choose_pivot(array, left, right):

            # first element
            return left

        def partition(array, left, right):
            p = key(array[left])
            i = left + 1
            for j in range(left + 1, right + 1):

                # Sort in increasing order
                if reverse == False:
                    if key(array[j]) < p:
                        swap(array, j, i)
                        i += 1
                
                # Sort in decreasing order
                else:    
                    if key(array[j]) > p:
                        swap(array, j, i)
                        i += 1
                

            # place pivot correctly
            swap(array, left, i - 1)

            # return final pivot position
            return i - 1

        if left >= right:
            return

        else:
            i = choose_pivot(array, left, right)
            swap(array, left, i)

            # new pivot position
            j = partition(array, left, right)

            # recurse on first part
            q_routine(array, left, j- 1)

            # recurse on second part
            q_routine(array, j + 1, right)

    left = 0
    right = len(array) - 1
    q_routine(array, left, right)


# Minimum spanning tree
# Return list of MST edges and list of remaining edges
def kruskal(nodes, edges):
    union_find = Union_find(nodes)
    
    quicksort(edges, key=lambda edge: edge.cost)
    
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
    

# Return max spacing and total cost with target number of clusters k
def clusters(nodes, edges, k):
    union_find = Union_find(nodes)
    
    quicksort(edges, key=lambda edge: edge.cost)
    
    # If graph has no edges:
    if not edges:
        max_spacing = None

    # Store chosen edges
    cluster_edges = []

    total_edges = len(edges)

    for i in range(total_edges):

        # Get first edge
        min_edge = edges[i]
        x, y = min_edge.word_u, min_edge.word_v

        if k == len(nodes):
            max_spacing = min_edge.cost
            break

        if union_find.union(x, y):
            cluster_edges.append(min_edge)

        # Once k clusters reached
        if union_find.clusters == k:
            if k == 1:
                max_spacing = None
            else:
                # Iterate through remaining edges until max spacing is found
                while True:
                    i += 1

                    # If no edges remain between clusters
                    if i == total_edges:
                        max_spacing = math.inf
                        break

                    next_edge = edges[i]
                    x, y = next_edge.word_u, next_edge.word_v
                    
                    # Check if nodes of edge are in different groups
                    if union_find.contents[union_find.find(x)].parent != \
                        union_find.contents[union_find.find(y)].parent:
                        max_spacing = next_edge.cost
                        break
            break

    # If all edges were iterated through without breaking
    else:
        return None

    # Calculate cost of all chosen edges
    total_cost = 0
    for edge in cluster_edges:
        total_cost += edge.cost
    
    # Make list of word clusters
    node_clusters_dict = {}
    for node in nodes:
        parent = union_find.find(node)
        if parent not in node_clusters_dict:
            node_clusters_dict[parent] = [node]
        else:
            node_clusters_dict[parent].append(node)
    
    clusters_list = [node_clusters_dict[parent] for parent in node_clusters_dict]

    return max_spacing, total_cost, clusters_list


# Run max-spacing k clustering on sentence for all possible values of k
def test_clusters(nodes, edges):

    # Store spacing / cost ratios to calculate mean and standard deviations
    ratio_list = []

    for k in range(len(nodes), 0, -1):
        results = clusters(nodes, edges, k)
        if not results:
            break
        max_spacing, total_cost, clusters_list = results
        ratio = max_spacing / total_cost if (max_spacing and total_cost) and \
            max_spacing != math.inf else None
        if ratio:
            ratio_list.append(ratio)    
        print("k = {}".format(k))
        for cluster in clusters_list:
            print("{", end=" ")
            for word in cluster:
                print(word.upper(), end=" ")
            print("}")
        print("max spacing: {}".format(max_spacing))
        print("total cost: {}".format(total_cost))
        print("spacing / cost = {}".format(ratio))
        print()
    
    # Calculate mean and standard deviation for ratios
    if ratio_list:
        mean = numpy.mean(ratio_list)
        median = numpy.median(ratio_list)
        minimum, maximum = min(ratio_list), max(ratio_list)
        standard_deviation = numpy.std(ratio_list)
        print("spacing / cost ratios:")
        print("mean: {}".format(mean))
        print("median: {}".format(median))
        print("min, max: {}, {}".format(minimum, maximum))
        print("standard deviation: {}".format(standard_deviation))
        print()

    print('_' * 50)
    print()
