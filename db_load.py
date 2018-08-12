import nltk
import sqlite3
import Stemmer
import time

stemmer = Stemmer.Stemmer('english')

# Set of stopwords
stop_words = set(nltk.corpus.stopwords.words('english'))


# Return list of sentences (each as a list of words) from the Gutenberg corpus
def get_sentences(document):
    if document in nltk.corpus.gutenberg.fileids():
        document_sentences = nltk.corpus.gutenberg.sents(document)
    elif document == 'brown':
        document_sentences = nltk.corpus.brown.sents()
    elif document == 'reuters':
        document_sentences = nltk.corpus.reuters.sents()
    else:
        print("Error: sentences for '{}' could not be loaded.".format(document))
        return None
    return document_sentences


# Make database tables
def make_db_tables(database):
    # Connect to database
    conn = sqlite3.connect(database)
    db = conn.cursor()

    # Make tables
    db.execute('''CREATE TABLE IF NOT EXISTS documents (
        name TEXT PRIMARY KEY
    )''')

    db.execute('''CREATE TABLE IF NOT EXISTS edges (
        word_u TEXT,
        word_v TEXT,
        count INT,
        PRIMARY KEY (word_u, word_v)
    )''')

    db.execute('''CREATE TABLE IF NOT EXISTS words (
        word TEXT PRIMARY KEY,
        count INT
    )''')

    conn.close()  


# Given list of document file names, scan words and update database
def load_corpus(database, document_names):
    start_total = time.time()

    # Make database if doesn't already exist
    make_db_tables(database)

    # Connect to database
    conn = sqlite3.connect(database)
    db = conn.cursor()

    # Get records of previously uploaded documents
    corpus_documents = list(db.execute("SELECT name FROM documents"))
    corpus_documents = [document_name[0] for document_name in \
        db.execute("SELECT name FROM documents")]
    print("corpus database contents: {}".format(corpus_documents))
    print()

    conn.close()

    new_documents = []
    for document in document_names:
        
        # If document has already been loaded, skip
        if document in corpus_documents:
            pass

        else:
            new_documents.append(document)

    if not new_documents:
        print("no documents were loaded")
        print()
        return None
    
    print("documents to load: {}".format(new_documents))
    print()

    # Load new documents into database
    for document in new_documents:
        start_document = time.time()
        print("loading {}...".format(document))
        load_document(database, document)
        print("    loaded {}!".format(document))
        print("        load time: {}".format(get_runtime(start_document)))
        print()

    print("Total loading time: {}".format(get_runtime(start_total)))
    print()


# If no sentences provided, get them using NLTK sents
def load_document(database, document_name, sentences=None):

    # Connect to database
    conn = sqlite3.connect(database)
    db = conn.cursor()

    # Convert document to list of sentences as lists of words
    if not sentences:
        document_sentences = get_sentences(document_name)
    else:
        document_sentences = sentences

    for sentence in document_sentences:

        # Get set of word stems in each sentence, filtering out stopwords
        sentence_stems = list(set([stemmer.stemWord(word).lower() for word in sentence \
            if word.lower() not in stop_words]))

        for i in range(len(sentence_stems)):
            word = sentence_stems[i]

            # Filter out punctuation
            if ord(word[0].lower()) not in range(ord('a'), ord('z') + 1) or \
                ord(word[-1].lower()) not in range(ord('a'), ord('z') + 1):
                continue

            # Update word's count in database
            db.execute("UPDATE words SET count = count + 1 WHERE word = ?", (word,))

            # If no update was made, insert word into database
            if not db.rowcount:
                db.execute("INSERT INTO words (word, count) VALUES (?, 1)", (word,))

            # Make edges to all neighbors following word in sentence (to avoid duplicate pairs)
            for neighbor in sentence_stems[i + 1:]:
                
                # Filter out punctuation
                if ord(neighbor[0].lower()) not in range(ord('a'), ord('z') + 1) or \
                    ord(neighbor[-1].lower()) not in range(ord('a'), ord('z') + 1):
                    continue

                sorted_words = sort_words([word, neighbor])

                # Update edge's count in database
                db.execute("UPDATE edges SET count = count + 1 \
                    WHERE word_u = ? AND word_v = ?", sorted_words)
                
                # If no update was made, insert edge into database
                if not db.rowcount:
                    db.execute("INSERT INTO edges (word_u, word_v, count) \
                        VALUES (?, ?, 1)", sorted_words)
        
    # Add document name to database
    db.execute("INSERT INTO documents (name) VALUES (?)", (document_name,))

    # Commit database transaction and close connection
    conn.commit()
    conn.close()


# Given two words, return them in a tuple sorted in alphabetical order
def sort_words(word_list):
    return tuple(sorted(word_list, key=lambda word: word.lower()))


# Given two words, return string "[word_u]--[word_v]" that can be loaded into trie
# Sorts the words in alphabetical order
def get_edge_string(word_u, word_v):
    sorted_words = tuple(sorted([word_u, word_v], key=lambda word: word.lower()))
    return  sorted_words[0] + "--" +  sorted_words[1], sorted_words


def print_runtime(start_time):
    runtime = time.time() - start_time
    if runtime < 1:
        print("load time: {} milliseconds".format(int(runtime * 100000) / 100))
    elif runtime < 60:
        print("load time: {} seconds".format(int(runtime * 100) / 100))
    else:
        print("load time: {} minutes {} seconds".format(int(runtime // 60), int(runtime % 60)))
    print()


# Return formatted string containing runtime
def get_runtime(start_time):
    runtime = time.time() - start_time
    if runtime < 1:
        return "{} milliseconds".format(int(runtime * 100000) / 100)
    elif runtime < 60:
        return "{} seconds".format(int(runtime * 100) / 100)
    else:
        return "{} minutes {} seconds".format(int(runtime // 60), int(runtime % 60))