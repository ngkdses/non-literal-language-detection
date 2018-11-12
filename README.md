# non-literal-language-detection


Tools for analyzing co-occurrence network built out of large natural language corpus.

hume.py contains request function allowing user to pull up subgraph from co-occurrence network and analyze it with max-spacing k-clustering algorithm (and is named after Bruno Latour and Genevieve Teil's proposed Hume Machine).

clusters.py contains code for union-find data structure, Kruskal's MST algorithm, and max-spacing k-clustering algorithm. Analyzes spacing/cost ratios with Numpy.

db_load.py creates database with Sqlite3 and loads it with processed corpus from NLTK. Converts corpus to word counts and word co-occurrence counts (number of times any two words occur in the same sentence together).

visualize_graph.py generates .png image of subgraph using pydot and Graphviz, with minimum spanning tree indicated in red.
