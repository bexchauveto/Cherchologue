#!/usr/bin/env python3
import os
from bs4 import BeautifulSoup
import nltk
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import WhitespaceTokenizer
import re
from collections import Counter
import json
from collections import OrderedDict
from pprint import pprint
import operator

if __name__ == "__main__":
    tokens = []
    for nom_fichier in os.listdir("/home/dorian/Documents/INSA/5 IL/Recherche d'Informations/RessourcesProjet/corpus-utf8"):
        print(nom_fichier)
        if nom_fichier != "D46.html" and nom_fichier != "D75.html" and nom_fichier != "D89.html"  and nom_fichier != "D45.html":
            stemmer = SnowballStemmer("french")
            soup = BeautifulSoup(open("/home/dorian/Documents/INSA/5 IL/Recherche d'Informations/RessourcesProjet/corpus-utf8/"+nom_fichier), "lxml")


            # kill all script and style elements
            for script in soup(["script", "style"]):
                script.extract()    # rip it out

            # get text
            text = soup.get_text()

            # break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)

            tokens += WhitespaceTokenizer().tokenize(text)
            print(tokens)

    nonPunct = re.compile('.*[A-Za-z].*')  # must contain a letter or digit
    filtered = [w for w in tokens if nonPunct.match(w)]

    counts = Counter(filtered)
    sorted_counts = sorted(counts.items(), key=operator.itemgetter(1), reverse=True)
    sorted_counts = OrderedDict(sorted_counts)

    # pprint(sorted_counts)


    with open("raw-index.json", 'w') as outfile:
        json.dump(sorted_counts, outfile, indent=4, sort_keys=False)
