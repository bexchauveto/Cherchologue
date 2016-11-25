#!/usr/bin/env python3
import os
from bs4 import BeautifulSoup
import nltk
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import WhitespaceTokenizer
from nltk.corpus import stopwords
import re
from collections import Counter
import json
from collections import OrderedDict
from pprint import pprint
import operator
import chardet
import urllib.request


class Mot:
    def __init__(self, mot, fichier):
        self.mot = mot
        self.nb_occ = 1
        self.fichiers = []
        self.fichiers.append([fichier,1])

    def ajouter_occurence(self,fichier):
        found = False
        for couple in self.fichiers:
            if couple[0] == fichier:
                couple[1] += 1
                self.nb_occ += 1
                found = True
                break
        if not found:
            self.fichiers.append([fichier,1])
            self.nb_occ += 1

    def __str__(self):
        ret = "{\"mot\":\"" + self.mot + "\",\"nb_occ\":" + str(self.nb_occ) + ",\"fichiers\":{"
        for fichier in self.fichiers:
            ret += "\"" + fichier[0] + "\":" + str(fichier[1]) + ","
        ret = ret[:-1]
        ret += "}}"
        return ret

class Document:
    def __init__(self, fichier):
        self.fichier = fichier
        self.mots = []

    def ajouter_mot(self,mot):
        found = False
        for couple in self.mots:
            if couple[0] == mot:
                couple[1] += 1
                found = True
                break
        if not found:
            self.mots.append([mot,1])

    def __str__(self):
        ret = "{\"fichier\":\"" + self.fichier + "\",\"mots\":{"
        for mot in self.mots:
            ret += "\"" + mot[0] + "\":" + str(mot[1]) + ","
        ret = ret[:-1]
        ret += "}}"
        return ret


if __name__ == "__main__":
    mots_a_ecrire = []
    fichiers_a_ecrire = []
    stopwords = ["Ap.", "Apr.", "GHz", "MHz", "USD", "a", "afin", "ah", "ai", "aie", "aient", "aies", "ait", "alors", "après", "as", "attendu", "au", "au-delà", "au-devant", "aucun", "aucune", "audit", "auprès", "auquel", "aura", "aurai", "auraient", "aurais", "aurait", "auras", "aurez", "auriez", "aurions", "aurons", "auront", "aussi", "autour", "autre", "autres", "autrui", "aux", "auxdites", "auxdits", "auxquelles", "auxquels", "avaient", "avais", "avait", "avant", "avec", "avez", "aviez", "avions", "avons", "ayant", "ayez", "ayons", "b", "bah", "banco", "ben", "bien", "bé", "c", "c'", "c'est", "c'était", "car", "ce", "ceci", "cela", "celle", "celle-ci", "celle-là", "celles", "celles-ci", "celles-là", "celui", "celui-ci", "celui-là", "celà", "cent", "cents", "cependant", "certain", "certaine", "certaines", "certains", "ces", "cet", "cette", "ceux", "ceux-ci", "ceux-là", "cf.", "cg", "cgr", "chacun", "chacune", "chaque", "chez", "ci", "cinq", "cinquante", "cinquante-cinq", "cinquante-deux", "cinquante-et-un", "cinquante-huit", "cinquante-neuf", "cinquante-quatre", "cinquante-sept", "cinquante-six", "cinquante-trois", "cl", "cm", "cm²", "comme", "contre", "d", "d'", "d'après", "d'un", "d'une", "dans", "de", "depuis", "derrière", "des", "desdites", "desdits", "desquelles", "desquels", "deux", "devant", "devers", "dg", "différentes", "différents", "divers", "diverses", "dix", "dix-huit", "dix-neuf", "dix-sept", "dl", "dm", "donc", "dont", "douze", "du", "dudit", "duquel", "durant", "dès", "déjà", "e", "eh", "elle", "elles", "en", "en-dehors", "encore", "enfin", "entre", "envers", "es", "est", "et", "eu", "eue", "eues", "euh", "eurent", "eus", "eusse", "eussent", "eusses", "eussiez", "eussions", "eut", "eux", "eûmes", "eût", "eûtes", "f", "fait", "fi", "flac", "fors", "furent", "fus", "fusse", "fussent", "fusses", "fussiez", "fussions", "fut", "fûmes", "fût", "fûtes", "g", "gr", "h", "ha", "han", "hein", "hem", "heu", "hg", "hl", "hm", "hm³", "holà", "hop", "hormis", "hors", "huit", "hum", "hé", "i", "ici", "il", "ils", "j", "j'", "j'ai", "j'avais", "j'étais", "jamais", "je", "jusqu'", "jusqu'au", "jusqu'aux", "jusqu'à", "jusque", "k", "kg", "km", "km²", "l", "l'", "l'autre", "l'on", "l'un", "l'une", "la", "laquelle", "le", "lequel", "les", "lesquelles", "lesquels", "leur", "leurs", "lez", "lors", "lorsqu'", "lorsque", "lui", "lès", "m", "m'", "ma", "maint", "mainte", "maintes", "maints", "mais", "malgré", "me", "mes", "mg", "mgr", "mil", "mille", "milliards", "millions", "ml", "mm", "mm²", "moi", "moins", "mon", "moyennant", "mt", "m²", "m³", "même", "mêmes", "n", "n'avait", "n'y", "ne", "neuf", "ni", "non", "nonante", "nonobstant", "nos", "notre", "nous", "nul", "nulle", "nº", "néanmoins", "o", "octante", "oh", "on", "ont", "onze", "or", "ou", "outre", "où", "p", "par", "par-delà", "parbleu", "parce", "parmi", "pas", "passé", "pendant", "personne", "peu", "plus", "plus_d'un", "plus_d'une", "plusieurs", "pour", "pourquoi", "pourtant", "pourvu", "près", "puisqu'", "puisque", "q", "qu", "qu'", "qu'elle", "qu'elles", "qu'il", "qu'ils", "qu'on", "quand", "quant", "quarante", "quarante-cinq", "quarante-deux", "quarante-et-un", "quarante-huit", "quarante-neuf", "quarante-quatre", "quarante-sept", "quarante-six", "quarante-trois", "quatorze", "quatre", "quatre-vingt", "quatre-vingt-cinq", "quatre-vingt-deux", "quatre-vingt-dix", "quatre-vingt-dix-huit", "quatre-vingt-dix-neuf", "quatre-vingt-dix-sept", "quatre-vingt-douze", "quatre-vingt-huit", "quatre-vingt-neuf", "quatre-vingt-onze", "quatre-vingt-quatorze", "quatre-vingt-quatre", "quatre-vingt-quinze", "quatre-vingt-seize", "quatre-vingt-sept", "quatre-vingt-six", "quatre-vingt-treize", "quatre-vingt-trois", "quatre-vingt-un", "quatre-vingt-une", "quatre-vingts", "que", "quel", "quelle", "quelles", "quelqu'", "quelqu'un", "quelqu'une", "quelque", "quelques", "quelques-unes", "quelques-uns", "quels", "qui", "quiconque", "quinze", "quoi", "quoiqu'", "quoique", "r", "revoici", "revoilà", "rien", "s", "s'", "sa", "sans", "sauf", "se", "seize", "selon", "sept", "septante", "sera", "serai", "seraient", "serais", "serait", "seras", "serez", "seriez", "serions", "serons", "seront", "ses", "si", "sinon", "six", "soi", "soient", "sois", "soit", "soixante", "soixante-cinq", "soixante-deux", "soixante-dix", "soixante-dix-huit", "soixante-dix-neuf", "soixante-dix-sept", "soixante-douze", "soixante-et-onze", "soixante-et-un", "soixante-et-une", "soixante-huit", "soixante-neuf", "soixante-quatorze", "soixante-quatre", "soixante-quinze", "soixante-seize", "soixante-sept", "soixante-six", "soixante-treize", "soixante-trois", "sommes", "son", "sont", "sous", "soyez", "soyons", "suis", "suite", "sur", "sus", "t", "t'", "ta", "tacatac", "tandis", "te", "tel", "telle", "telles", "tels", "tes", "toi", "ton", "toujours", "tous", "tout", "toute", "toutefois", "toutes", "treize", "trente", "trente-cinq", "trente-deux", "trente-et-un", "trente-huit", "trente-neuf", "trente-quatre", "trente-sept", "trente-six", "trente-trois", "trois", "très", "tu", "u", "un", "une", "unes", "uns", "v", "vers", "via", "vingt", "vingt-cinq", "vingt-deux", "vingt-huit", "vingt-neuf", "vingt-quatre", "vingt-sept", "vingt-six", "vingt-trois", "vis-à-vis", "voici", "voilà", "vos", "votre", "vous", "w", "x", "y", "z", "zéro", "à", "ç'", "ça", "ès", "étaient", "étais", "était", "étant", "étiez", "étions", "été", "étée", "étées", "étés", "êtes", "être", "ô"]
    stops = []
    for stopword in stopwords:
        stops.append(stopword.lower())
    for nom_fichier in os.listdir("../RessourcesProjet/corpus-utf8"):
        fichier = Document(nom_fichier)
        tokens = []
        with urllib.request.urlopen("file:///home/dorian/Documents/INSA/5IL/Recherche d'Informations/RessourcesProjet/corpus-utf8/" + nom_fichier) as url:
            rawdata = url.read()
        encodage = chardet.detect(rawdata)["encoding"]
        print(nom_fichier + " (" + encodage + ")")
        stemmer = SnowballStemmer("french")
        soup = BeautifulSoup(open("../RessourcesProjet/corpus-utf8/"+nom_fichier, encoding=encodage), "lxml", from_encoding=encodage)


        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()    # rip it out

        # get text
        text = soup.get_text().lower()

        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)

        tokens += WhitespaceTokenizer().tokenize(text)
        # We remove the stop words
        tokens = [token for token in tokens if token not in stops]
        # print(tokens)
        nonPunct = re.compile('^[A-Za-z]+$')  # must contain a letter or digit
        filtered = [w for w in tokens if nonPunct.match(w)]

        for mot in filtered:
            nouveau_mot = Mot(mot, nom_fichier)
            trouve = False
            for mot_present in mots_a_ecrire:
                if mot_present.mot == mot:
                    mot_present.ajouter_occurence(nom_fichier)
                    trouve = True
                    break
            if not trouve:
                mots_a_ecrire.append(nouveau_mot)
            fichier.ajouter_mot(mot)

        fichiers_a_ecrire.append(fichier)

    output = "{"
    for mot in mots_a_ecrire:
        output += str(mot) + ", \n"
    output = output[:-3]
    output += "}"

    outfile = open("index.json", 'w')
    outfile.write(output)

    output = "{"
    for fichier in fichiers_a_ecrire:
        output += str(fichier) + ", \n"
    output = output[:-3]
    output += "}"

    outfile = open("index-reverse.json", 'w')
    outfile.write(output)
