import clusters
import db_load2
import nltk
import sqlite3
import Stemmer
import sys
import visualize_graph

stemmer = Stemmer.Stemmer('english')


class Edge:
    def __init__(self, word_u, word_v, cost):
        self.word_u = word_u
        self.word_v = word_v
        self.cost = cost


# Given two words, return them in a tuple sorted in alphabetical order
def sort_words(word_list):
    return tuple(sorted(word_list, key=lambda word: word.lower()))


# Return inverse of coefficient of equivalence
def get_cost(u_count, v_count, edge_count):
    return (u_count * v_count) / (edge_count ** 2)


# Request either edges or connections from a single word
def make_request(database):

    # Given tuple of words, get edge cost
    def calculate_cost(word_tuple, alerts=False):
        # Get word counts
        word_counts = list(db.execute("SELECT count FROM words \
            WHERE word = ? OR word = ?", word_tuple))
        
        # If either or both words don't exist
        if len(word_counts) != 2:
            if alerts:
                print("word(s) not in database")
                print('_' * 50)
                print()
            return None

        # Get edge count, restarting search if it doesn't exist
        edge_count = list(db.execute("SELECT count FROM edges \
            WHERE word_u = ? AND word_v = ?", sort_words(word_tuple)))
        if not edge_count:
            if alerts:
                print("edge does not exist")
                print('_' * 50)
                print()
            return None
        
        edge_count = edge_count[0][0]
        
        # Calculate edge cost
        cost = get_cost(word_counts[0][0], word_counts[1][0], edge_count)

        return cost

    # Connect to database
    conn = sqlite3.connect(database)
    db = conn.cursor()

    print("Usage: [word] or [word_1 word_2]")
    print("Enter 'q' to quit")
    print('_' * 50)
    print()
    
    # Until user quits
    while True:
        request = input("Request: ").split()
        print()

        if not request:
            continue

        # If 'q', quit
        if request[0] == 'q':
            print('_' * 50)
            print()
            return None
        
        # Get stems
        request_stems = tuple([stemmer.stemWord(word).lower() for word in request \
            if word.lower() not in db_load2.stop_words])

        # If two words submitted, get edge
        if len(request_stems) == 2:
            cost = calculate_cost(request_stems, alerts=True)
            if not cost:
                continue
        
            print("{} -- {}: cost = {}".format(
                request_stems[0].upper(), request_stems[1].upper(), cost))
            print('_' * 50)
            print()

        # If only one term provided, print that word's count
        elif len(request_stems) == 1:
            word_count = list(db.execute("SELECT count FROM words \
                WHERE word = ?", request_stems))
            if not word_count:
                print("word does not exist")
                print('_' * 50)
                print()
                continue
            print("{}: {} occurrences".format(request_stems[0].upper(), word_count[0][0]))
            print('_' * 50)
            print()
        
        # If more than two words (i.e. sentence) provided
        elif len(request_stems) > 2:
            sentence_words = [word for word in set(request_stems) if \
                list(db.execute("SELECT word FROM words WHERE word = ?", (word,)))]

            # Generate list of edges to represent every word pair in sentence_words          
            edges = []
            for i in range(len(sentence_words)):
                word = sentence_words[i]
                for neighbor in sentence_words[i + 1:]:
                    cost = calculate_cost((word, neighbor))
                    if cost:
                        edges.append(Edge(word, neighbor, cost))
        
            # Write PNG visualization of graph
            visualize_graph.visualize_graph(sentence_words, edges)    

            clusters.test_clusters(sentence_words, edges)
    
    conn.close()


def main():
    print()

    if len(sys.argv) == 1:
        corpus_database = input("Database: ")
        print()
    else:
        corpus_database = sys.argv[1]

    gutenberg_corpus = ['melville-moby_dick.txt','austen-emma.txt', 'bible-kjv.txt', \
        'austen-sense.txt', 'austen-persuasion.txt', 'bryant-stories.txt', \
        'burgess-busterbrown.txt', 'chesterton-ball.txt', 'chesterton-brown.txt', \
        'chesterton-thursday.txt', 'edgeworth-parents.txt']

    db_load2.load_corpus(corpus_database, gutenberg_corpus)

    make_request(corpus_database)


if __name__ == "__main__":
    main()