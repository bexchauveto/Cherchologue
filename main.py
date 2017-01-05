#!/usr/bin/env python3
import os
import sys
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
import math
import sparql_client


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
        self.nb_de_mots = 0

    def ajouter_mot(self,mot):
        found = False
        self.nb_de_mots += 1
        for couple in self.mots:
            if couple[0] == mot:
                couple[1] += 1
                found = True
                break
        if not found:
            self.mots.append([mot,1])

    def __str__(self):
        ret = "{\"fichier\":\"" + self.fichier + "\",\"nb_de_mots\":" + str(self.nb_de_mots) + ",\"mots\":{"
        for mot in self.mots:
            ret += "\"" + mot[0] + "\":" + str(mot[1]) + ","
        ret = ret[:-1]
        ret += "}}"
        return ret


def indexer():
    mots_a_ecrire = []
    fichiers_a_ecrire = []
    nb_de_mots_total = 0
    stopwords = ["Ap.", "Apr.", "GHz", "MHz", "USD", "a", "afin", "ah", "ai", "aie", "aient", "aies", "ait", "alors", "après", "as", "attendu", "au", "au-delà", "au-devant", "aucun", "aucune", "audit", "auprès", "auquel", "aura", "aurai", "auraient", "aurais", "aurait", "auras", "aurez", "auriez", "aurions", "aurons", "auront", "aussi", "autour", "autre", "autres", "autrui", "aux", "auxdites", "auxdits", "auxquelles", "auxquels", "avaient", "avais", "avait", "avant", "avec", "avez", "aviez", "avions", "avons", "ayant", "ayez", "ayons", "b", "bah", "banco", "ben", "bien", "bé", "c", "c'", "c'est", "c'était", "car", "ce", "ceci", "cela", "celle", "celle-ci", "celle-là", "celles", "celles-ci", "celles-là", "celui", "celui-ci", "celui-là", "celà", "cent", "cents", "cependant", "certain", "certaine", "certaines", "certains", "ces", "cet", "cette", "ceux", "ceux-ci", "ceux-là", "cf.", "cg", "cgr", "chacun", "chacune", "chaque", "chez", "ci", "cinq", "cinquante", "cinquante-cinq", "cinquante-deux", "cinquante-et-un", "cinquante-huit", "cinquante-neuf", "cinquante-quatre", "cinquante-sept", "cinquante-six", "cinquante-trois", "cl", "cm", "cm²", "comme", "contre", "d", "d'", "d'après", "d'un", "d'une", "dans", "de", "depuis", "derrière", "des", "desdites", "desdits", "desquelles", "desquels", "deux", "devant", "devers", "dg", "différentes", "différents", "divers", "diverses", "dix", "dix-huit", "dix-neuf", "dix-sept", "dl", "dm", "donc", "dont", "douze", "du", "dudit", "duquel", "durant", "dès", "déjà", "e", "eh", "elle", "elles", "en", "en-dehors", "encore", "enfin", "entre", "envers", "es", "est", "et", "eu", "eue", "eues", "euh", "eurent", "eus", "eusse", "eussent", "eusses", "eussiez", "eussions", "eut", "eux", "eûmes", "eût", "eûtes", "f", "fait", "fi", "flac", "fors", "furent", "fus", "fusse", "fussent", "fusses", "fussiez", "fussions", "fut", "fûmes", "fût", "fûtes", "g", "gr", "h", "ha", "han", "hein", "hem", "heu", "hg", "hl", "hm", "hm³", "holà", "hop", "hormis", "hors", "huit", "hum", "hé", "i", "ici", "il", "ils", "j", "j'", "j'ai", "j'avais", "j'étais", "jamais", "je", "jusqu'", "jusqu'au", "jusqu'aux", "jusqu'à", "jusque", "k", "kg", "km", "km²", "l", "l'", "l'autre", "l'on", "l'un", "l'une", "la", "laquelle", "le", "lequel", "les", "lesquelles", "lesquels", "leur", "leurs", "lez", "lors", "lorsqu'", "lorsque", "lui", "lès", "m", "m'", "ma", "maint", "mainte", "maintes", "maints", "mais", "malgré", "me", "mes", "mg", "mgr", "mil", "mille", "milliards", "millions", "ml", "mm", "mm²", "moi", "moins", "mon", "moyennant", "mt", "m²", "m³", "même", "mêmes", "n", "n'avait", "n'y", "ne", "neuf", "ni", "non", "nonante", "nonobstant", "nos", "notre", "nous", "nul", "nulle", "nº", "néanmoins", "o", "octante", "oh", "on", "ont", "onze", "or", "ou", "outre", "où", "p", "par", "par-delà", "parbleu", "parce", "parmi", "pas", "passé", "pendant", "personne", "peu", "plus", "plus_d'un", "plus_d'une", "plusieurs", "pour", "pourquoi", "pourtant", "pourvu", "près", "puisqu'", "puisque", "q", "qu", "qu'", "qu'elle", "qu'elles", "qu'il", "qu'ils", "qu'on", "quand", "quant", "quarante", "quarante-cinq", "quarante-deux", "quarante-et-un", "quarante-huit", "quarante-neuf", "quarante-quatre", "quarante-sept", "quarante-six", "quarante-trois", "quatorze", "quatre", "quatre-vingt", "quatre-vingt-cinq", "quatre-vingt-deux", "quatre-vingt-dix", "quatre-vingt-dix-huit", "quatre-vingt-dix-neuf", "quatre-vingt-dix-sept", "quatre-vingt-douze", "quatre-vingt-huit", "quatre-vingt-neuf", "quatre-vingt-onze", "quatre-vingt-quatorze", "quatre-vingt-quatre", "quatre-vingt-quinze", "quatre-vingt-seize", "quatre-vingt-sept", "quatre-vingt-six", "quatre-vingt-treize", "quatre-vingt-trois", "quatre-vingt-un", "quatre-vingt-une", "quatre-vingts", "que", "quel", "quelle", "quelles", "quelqu'", "quelqu'un", "quelqu'une", "quelque", "quelques", "quelques-unes", "quelques-uns", "quels", "qui", "quiconque", "quinze", "quoi", "quoiqu'", "quoique", "r", "revoici", "revoilà", "rien", "s", "s'", "sa", "sans", "sauf", "se", "seize", "selon", "sept", "septante", "sera", "serai", "seraient", "serais", "serait", "seras", "serez", "seriez", "serions", "serons", "seront", "ses", "si", "sinon", "six", "soi", "soient", "sois", "soit", "soixante", "soixante-cinq", "soixante-deux", "soixante-dix", "soixante-dix-huit", "soixante-dix-neuf", "soixante-dix-sept", "soixante-douze", "soixante-et-onze", "soixante-et-un", "soixante-et-une", "soixante-huit", "soixante-neuf", "soixante-quatorze", "soixante-quatre", "soixante-quinze", "soixante-seize", "soixante-sept", "soixante-six", "soixante-treize", "soixante-trois", "sommes", "son", "sont", "sous", "soyez", "soyons", "suis", "suite", "sur", "sus", "t", "t'", "ta", "tacatac", "tandis", "te", "tel", "telle", "telles", "tels", "tes", "toi", "ton", "toujours", "tous", "tout", "toute", "toutefois", "toutes", "treize", "trente", "trente-cinq", "trente-deux", "trente-et-un", "trente-huit", "trente-neuf", "trente-quatre", "trente-sept", "trente-six", "trente-trois", "trois", "très", "tu", "u", "un", "une", "unes", "uns", "v", "vers", "via", "vingt", "vingt-cinq", "vingt-deux", "vingt-huit", "vingt-neuf", "vingt-quatre", "vingt-sept", "vingt-six", "vingt-trois", "vis-à-vis", "voici", "voilà", "vos", "votre", "vous", "w", "x", "y", "z", "zéro", "à", "ç'", "ça", "ès", "étaient", "étais", "était", "étant", "étiez", "étions", "été", "étée", "étées", "étés", "êtes", "être", "ô"]
    stops = []
    for stopword in stopwords:
        stops.append(stopword.lower())
    nb_docs = len(os.listdir("../RessourcesProjet/corpus-utf8"))
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

        nb_de_mots_total += len(filtered)

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

    output = "{\"mots\":["
    for mot in mots_a_ecrire:
        output += str(mot) + ", \n"
    output = output[:-3]
    output += "]}"

    outfile = open("index.json", 'w')
    outfile.write(output)

    output = "{\"documents\":["
    for fichier in fichiers_a_ecrire:
        output += str(fichier) + ", \n"
    output = output[:-3]
    output += "],\n\"nb_de_mots_total\":" + str(nb_de_mots_total) + ",\n\"nb_mots_moyen\":" + str(nb_de_mots_total/nb_docs) + "}"

    outfile = open("index-reverse.json", 'w')
    outfile.write(output)

def requete_mots_clefs(requete):
    index_file = open("index.json", 'r')
    index = json.load(index_file)
    pprint(index)

def get_nb_de_mots(nom_fichier):
    index_reverse_file = open("index-reverse.json", 'r')
    index_reverse = json.load(index_reverse_file)
    for fichier in index_reverse["documents"]:
        if fichier["fichier"] == nom_fichier:
            return fichier["nb_de_mots"]

def requete_tf_naif(requete):
    index_file = open("index.json", 'r')
    index = json.load(index_file)
    index_reverse_file = open("index-reverse.json", 'r')
    index_reverse = json.load(index_reverse_file)
    ponderations = []
    ponderations_tf = []
    for mot_recherche in requete.split():
        fichiers_ordonnes = []
        for mot in index["mots"]:
            if mot["mot"] == mot_recherche:
                fichiers_ordonnes = sorted(mot['fichiers'].items(), key=operator.itemgetter(1), reverse=True)
        ponderations_mot_courant = []
        for i in range(0, len(fichiers_ordonnes)):
            if i == 0:
                ponderations_mot_courant.append((fichiers_ordonnes[i][0],1))
            else:
                if (fichiers_ordonnes[i][1] == fichiers_ordonnes[i-1][1]):
                    ponderations_mot_courant.append((fichiers_ordonnes[i][0],ponderations_mot_courant[i-1][1]))
                else:
                    ponderations_mot_courant.append((fichiers_ordonnes[i][0],ponderations_mot_courant[i-1][1]+1))
        ponderations.append(ponderations_mot_courant)
        ponderations_tf.append(fichiers_ordonnes)

    liste_fichiers = []
    for fichier in index_reverse["documents"]:
        liste_fichiers.append(fichier["fichier"])

    ponderation_finale = [[0 for x in range(0,len(requete.split()))] for y in range(0,len(liste_fichiers))]
    for i in range(0, len(liste_fichiers)):
        for j in range(0, len(requete.split())):
            for k in range(0,len(ponderations[j])):
                if liste_fichiers[i] == ponderations[j][k][0]:
                    ponderation_finale[i][j] = ponderations[j][k][1]
            if ponderation_finale[i][j] == 0:
                ponderation_finale[i][j] = ponderations[j][-1][1]+1

    ponderation_tf_finale = [[(liste_fichiers[y],0) for x in range(0,len(requete.split()))] for y in range(0,len(liste_fichiers))]
    for i in range(0, len(liste_fichiers)):
        for j in range(0, len(requete.split())):
            for k in range(0,len(ponderations_tf[j])):
                if liste_fichiers[i] == ponderations_tf[j][k][0]:
                    ponderation_tf_finale[i][j] = (ponderations_tf[j][k][0],ponderations_tf[j][k][1])

    fichiers_ponderes = []
    for i in range(0, len(liste_fichiers)):
        somme_ponderations = 0
        ponderation_max = 0
        for j in range(0, len(requete.split())):
            somme_ponderations += ponderation_finale[i][j]
            ponderation_max += ponderations[j][-1][1]
        if somme_ponderations <= ponderation_max:
            fichiers_ponderes.append((liste_fichiers[i],1))
        else:
            fichiers_ponderes.append((liste_fichiers[i],0))
        # fichiers_ponderes.append((liste_fichiers[i],somme_ponderations))

    outfile = open("result-tf-naif.json", 'w')
    outfile.write(json.dumps(fichiers_ponderes))

    return ponderation_tf_finale


def requete_tf_robertson(requete):
    index_file = open("index.json", 'r')
    index = json.load(index_file)
    index_reverse_file = open("index-reverse.json", 'r')
    index_reverse = json.load(index_reverse_file)
    ponderations = []
    ponderations_tf = []
    for mot_recherche in requete.split():
        fichiers_ordonnes = []
        for mot in index["mots"]:
            if mot["mot"] == mot_recherche:
                fichiers_ordonnes = sorted(mot['fichiers'].items(), key=operator.itemgetter(1), reverse=True)
                tf = {}
                for value in fichiers_ordonnes:
                    tf[value[0]] = value[1]/(0.5+1.5*(get_nb_de_mots(value[0])/index_reverse['nb_mots_moyen'])+value[1])
        fichiers_ordonnes = sorted(tf.items(), key=operator.itemgetter(1), reverse=True)
        ponderations_mot_courant = []
        for i in range(0, len(fichiers_ordonnes)):
            # fichiers_ordonnes[i][0] : nom du fichier
            # fichiers_ordonnes[i][1] : occurence du mot recherché
            if i == 0:
                ponderations_mot_courant.append((fichiers_ordonnes[i][0],1))
            else:
                if (fichiers_ordonnes[i][1] == fichiers_ordonnes[i-1][1]):
                    ponderations_mot_courant.append((fichiers_ordonnes[i][0],ponderations_mot_courant[i-1][1]))
                else:
                    ponderations_mot_courant.append((fichiers_ordonnes[i][0],ponderations_mot_courant[i-1][1]+1))
        ponderations.append(ponderations_mot_courant)
        ponderations_tf.append(fichiers_ordonnes)
    # pprint(ponderations_tf)
    liste_fichiers = []
    for fichier in index_reverse["documents"]:
        liste_fichiers.append(fichier["fichier"])

    ponderation_finale = [[0 for x in range(0,len(requete.split()))] for y in range(0,len(liste_fichiers))]
    for i in range(0, len(liste_fichiers)):
        for j in range(0, len(requete.split())):
            for k in range(0,len(ponderations[j])):
                if liste_fichiers[i] == ponderations[j][k][0]:
                    ponderation_finale[i][j] = ponderations[j][k][1]
            if ponderation_finale[i][j] == 0:
                ponderation_finale[i][j] = ponderations[j][-1][1]+1

    ponderation_tf_finale = [[(liste_fichiers[y],0) for x in range(0,len(requete.split()))] for y in range(0,len(liste_fichiers))]
    for i in range(0, len(liste_fichiers)):
        for j in range(0, len(requete.split())):
            for k in range(0,len(ponderations_tf[j])):
                if liste_fichiers[i] == ponderations_tf[j][k][0]:
                    ponderation_tf_finale[i][j] = (ponderations_tf[j][k][0],ponderations_tf[j][k][1])

    fichiers_ponderes = []
    for i in range(0, len(liste_fichiers)):
        somme_ponderations = 0
        ponderation_max = 0
        for j in range(0, len(requete.split())):
            somme_ponderations += ponderation_finale[i][j]
            ponderation_max += ponderations[j][-1][1]
        if somme_ponderations <= ponderation_max:
            fichiers_ponderes.append((liste_fichiers[i],1))
        else:
            fichiers_ponderes.append((liste_fichiers[i],0))
        # fichiers_ponderes.append((liste_fichiers[i],somme_ponderations))

    outfile = open("result-tf-robertson.json", 'w')
    outfile.write(json.dumps(fichiers_ponderes))

    return ponderation_tf_finale

def calculIDF(mot_requete):
    index_file = open("index.json", 'r')
    index = json.load(index_file)
    index_reverse_file = open("index-reverse.json", 'r')
    index_reverse = json.load(index_reverse_file)
    for mot in index["mots"]:
        if mot_requete == mot["mot"]:
            return math.log(len(index_reverse["documents"])/len(mot["fichiers"]))

def calculTFIDF(tf, idf):
    tfidf = {}
    for i in range(0, len(tf)):
        tmp = 0
        for j in range(0, len(idf)):
            tmp += tf[i][j][1]*idf[j]
        tfidf[tf[i][0][0]] = tmp
    return sorted(tfidf.items(), key=operator.itemgetter(1), reverse=True);

def calculPS(tfidf, idf):
    ps = {}
    for i in range(0, len(tfidf)):
        tmp = 0
        for j in range(0, len(idf)):
            tmp += tfidf[i][1]*idf[j]
        ps[tfidf[i][0]] = tmp
    return sorted(ps.items(), key=operator.itemgetter(1), reverse=True);

def calculCD(tfidf, idf):
    cd = {}
    for i in range(0, len(tfidf)):
        tmp = 0
        for j in range(0, len(idf)):
            if tfidf[i][1] == 0 or idf[j] == 0 :
                tmp = 0
            else :
                tmp += (2*(tfidf[i][1]*idf[j])/((tfidf[i][1]*tfidf[i][1])+(idf[j]*idf[j])))
        cd[tfidf[i][0]] = tmp
    return sorted(cd.items(), key=operator.itemgetter(1), reverse=True);

def calculCOS(tfidf, idf):
    cos = {}
    for i in range(0, len(tfidf)):
        tmp = 0
        for j in range(0, len(idf)):
            if tfidf[i][1] == 0 or idf[j] == 0 :
                tmp = 0
            else :
                tmp += ((tfidf[i][1]*idf[j])/(math.sqrt((tfidf[i][1]*tfidf[i][1])+(idf[j]*idf[j]))))
        cos[tfidf[i][0]] = tmp
    return sorted(cos.items(), key=operator.itemgetter(1), reverse=True);

def calculJACCARD(tfidf, idf):
    jac = {}
    for i in range(0, len(tfidf)):
        tmp = 0
        for j in range(0, len(idf)):
            if tfidf[i][1] == 0 or idf[j] == 0 :
                tmp = 0
            else :
                tmp += ((tfidf[i][1]*idf[j])/((tfidf[i][1]*tfidf[i][1])+(idf[j]*idf[j])-(tfidf[i][1]*idf[j])))
        jac[tfidf[i][0]] = tmp
    return sorted(jac.items(), key=operator.itemgetter(1), reverse=True);

if __name__ == "__main__":
    sparql_client.ask("""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?label
        WHERE { <http://dbpedia.org/resource/Asturias> rdfs:label ?label }
    """)

    tf = []
    idf = []
    tfidf = {}
    requete_liste = ["personnes intouchables", "lieunaissance omar sy","premiere récompence intouchables", "palmares globes de cristal 2012","membre jury globes de cristal 2012","prix omar sy globes de cristal 2012","lieu globes cristal 2012", "prix omar sy","acteur joué avec omar sy","prix enfant de Trappes", "personne a joué avec Omar Sy"]
    requete = ""
    pprint(sys.argv)
    if len(sys.argv) > 1:
        if ("-q1" in sys.argv):
            requete = requete_liste[0]
        if ("-q2" in sys.argv):
            requete = requete_liste[1]
        if ("-q3" in sys.argv):
            requete = requete_liste[2]
        if ("-q4" in sys.argv):
            requete = requete_liste[3]
        if ("-q5" in sys.argv):
            requete = requete_liste[4]
        if ("-q6" in sys.argv):
            requete = requete_liste[5]
        if ("-q7" in sys.argv):
            requete = requete_liste[6]
        if ("-q8" in sys.argv):
            requete = requete_liste[7]
        if ("-q9" in sys.argv):
            requete = requete_liste[8]
        if ("-q10" in sys.argv):
            requete = requete_liste[9]
        if ("-q11" in sys.argv):
            requete = requete_liste[10]
        if ("--generate-index" in sys.argv) or ("-g" in sys.argv):
            indexer()
        if ("--tf-naif" in sys.argv) or ("-tfn" in sys.argv):
            if requete == "":
                requete = input("[TF-Naïf] Entrez ce que vous cherchez : ")
            print("[TF-Naïf] Calcul du TF-Naïf en cours...")
            tf = requete_tf_naif(requete)
            print("[TF-Naïf] Calcul du TF-Naïf finis")
        if ("--tf-robertson" in sys.argv) or ("-tfr" in sys.argv):
            if requete == "":
                requete = input("[TF-Robertson] Entrez ce que vous cherchez : ")
            print("[TF-Robertson] Calcul du TF-Robertson en cours...")
            tf = requete_tf_robertson(requete)
            print("[TF-Robertson] Calcul du TF-Robertson finis")
        if ("-idf" in sys.argv):
            print("[IDF] Calcul de l'IDF en cours...")
            for mot in requete.split():
                idf.append(calculIDF(mot))
            print("[IDF] Calcul de l'IDF finis")
            print("[TF.IDF] Calcul de TF.IDF en cours...")
            tfidf = calculTFIDF(tf, idf)
            print("[TF.IDF] Calcul de TF.IDF finis")
        if ("-ps" in sys.argv):
            print("[PS] Calcul du PS en cours...")
            resultat = calculPS(tfidf, idf)
            print("[PS] Calcul du PS finis")
        if ("-cd" in sys.argv):
            print("[CD] Calcul du CD en cours...")
            resultat = calculCD(tfidf, idf)
            print("[CD] Calcul du CD finis")
        if ("-cos" in sys.argv):
            print("[COS] Calcul du COS en cours...")
            resultat = calculCOS(tfidf, idf)
            print("[COS] Calcul du COS finis")
        if ("-jac" in sys.argv):
            print("[JACCARD] Calcul du JACCARD en cours...")
            resultat = calculJACCARD(tfidf, idf)
            print("[JACCARD] Calcul du JACCARD finis")

    name = ""
    for i in range(1,len(sys.argv)):
        name += sys.argv[i]
    outfile = open("result"+name+".json",'w')
    outfile.write(json.dumps(resultat))
