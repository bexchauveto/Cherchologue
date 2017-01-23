#!/usr/bin/env python3
import os
import sys
import re
import json
from pprint import pprint
import operator
import urllib.request
import math
from __future__ import print_function
from SPARQLWrapper import SPARQLWrapper, JSON
import chardet
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import WhitespaceTokenizer
from bs4 import BeautifulSoup


class Mot(object):
    """
    Objet mot
    """
    def __init__(self, mot, fichier):
        """
        Fonction init
        """
        self.mot = mot
        self.nb_occ = 1
        self.fichiers = []
        self.fichiers.append([fichier, 1])

    def ajouter_occurence(self, fichier):
        """
        Fonction ajouter occurence
        """
        found = False
        for couple in self.fichiers:
            if couple[0] == fichier:
                couple[1] += 1
                self.nb_occ += 1
                found = True
                break
        if not found:
            self.fichiers.append([fichier, 1])
            self.nb_occ += 1

    def __str__(self):
        """
        Fonction str
        """
        ret = "{\"mot\":\"" + self.mot + "\", \"nb_occ\":" + str(self.nb_occ) + ", \"fichiers\":{"
        for fichier in self.fichiers:
            ret += "\"" + fichier[0] + "\":" + str(fichier[1]) + ", "
        ret = ret[:-1]
        ret += "}}"
        return ret

class Document(object):
    """
    objet Document
    """
    def __init__(self, fichier):
        """
        Fonction init
        """
        self.fichier = fichier
        self.mots = []
        self.nb_de_mots = 0

    def ajouter_mot(self, mot):
        """
        Fonction ajouter mot
        """
        found = False
        self.nb_de_mots += 1
        for couple in self.mots:
            if couple[0] == mot:
                couple[1] += 1
                found = True
                break
        if not found:
            self.mots.append([mot, 1])

    def __str__(self):
        """
        Fonction str
        """
        ret = "{\"fichier\":\"" + self.fichier + "\", \"nb_de_mots\":" + str(self.nb_de_mots) + \
              ", \"mots\":{"
        for mot in self.mots:
            ret += "\"" + mot[0] + "\":" + str(mot[1]) + ", "
        ret = ret[:-1]
        ret += "}}"
        return ret


def indexer():
    """
    Fonction indexer
    """
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
        with urllib.request.urlopen("file:///home/dorian/Documents/INSA/5IL/ \
                                     Recherche d'Informations/RessourcesProjet/corpus-utf8/"  \
                                     + nom_fichier) as url:
            rawdata = url.read()
        encodage = chardet.detect(rawdata)["encoding"]
        print(nom_fichier + " (" + encodage + ")")
        stemmer = SnowballStemmer("french")
        soup = BeautifulSoup(open("../RessourcesProjet/corpus-utf8/"+nom_fichier,  \
                             encoding=encodage), "lxml", from_encoding=encodage)


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
    output += "], \n\"nb_de_mots_total\":" + str(nb_de_mots_total) + ", \n\"nb_mots_moyen\":" + \
              str(nb_de_mots_total/nb_docs) + "}"

    outfile = open("index-reverse.json", 'w')
    outfile.write(output)

def requete_mots_clefs(requete):
    """
    Fonction requete mots clefs
    """
    index_file = open("index.json", 'r')
    index = json.load(index_file)
    pprint(index)

def get_nb_de_mots(nom_fichier):
    """
    Fonction get nb de mots
    """
    index_reverse_file = open("index-reverse.json", 'r')
    index_reverse = json.load(index_reverse_file)
    for fichier in index_reverse["documents"]:
        if fichier["fichier"] == nom_fichier:
            return fichier["nb_de_mots"]

def requete_tf_naif(requete):
    """
    Fonction requete tf naif
    """
    index_file = open("index.json", 'r')
    index = json.load(index_file)
    index_reverse_file = open("index-reverse.json", 'r')
    index_reverse = json.load(index_reverse_file)
    ponderations = []
    ponderations_tf = []

    liste_fichiers = []
    for fichier in index_reverse["documents"]:
        liste_fichiers.append(fichier["fichier"])

    for mot_recherche in requete.split():
        fichiers_ordonnes = []
        for mot in index["mots"]:
            if mot["mot"] == mot_recherche:
                fichiers_ordonnes = sorted(mot['fichiers'].items(), key=operator.itemgetter(1), \
                                           reverse=True)
        ponderations_mot_courant = []
        for i in range(0, len(fichiers_ordonnes)):
            if i == 0:
                ponderations_mot_courant.append((fichiers_ordonnes[i][0], 1))
            else:
                if fichiers_ordonnes[i][1] == fichiers_ordonnes[i-1][1]:
                    ponderations_mot_courant.append((fichiers_ordonnes[i][0], \
                                                     ponderations_mot_courant[i-1][1]))
                else:
                    ponderations_mot_courant.append((fichiers_ordonnes[i][0], \
                                                     ponderations_mot_courant[i-1][1]+1))

        if ponderations_mot_courant == []:
            for i in range(0, len(liste_fichiers)):
                ponderations_mot_courant.append((liste_fichiers[i][0], 0))

        ponderations.append(ponderations_mot_courant)
        ponderations_tf.append(fichiers_ordonnes)



    ponderation_finale = [[(x-x+y-y) for x in range(0, len(requete.split()))] \
                             for y in range(0, len(liste_fichiers))]
    for i in range(0, len(liste_fichiers)):
        for j in range(0, len(requete.split())):
            for k in range(0, len(ponderations[j])):
                if liste_fichiers[i] == ponderations[j][k][0]:
                    ponderation_finale[i][j] = ponderations[j][k][1]
            if ponderation_finale[i][j] == 0:
                #if len(ponderations[j]) > 0:
                ponderation_finale[i][j] = ponderations[j][-1][1]+1

    ponderation_tf_finale = [[(liste_fichiers[y], (x-x)) for x in range(0, len(requete.split()))] \
                                                     for y in range(0, len(liste_fichiers))]
    for i in range(0, len(liste_fichiers)):
        for j in range(0, len(requete.split())):
            for k in range(0, len(ponderations_tf[j])):
                if liste_fichiers[i] == ponderations_tf[j][k][0]:
                    ponderation_tf_finale[i][j] = (ponderations_tf[j][k][0], \
                                                   ponderations_tf[j][k][1])

    fichiers_ponderes = []
    for i in range(0, len(liste_fichiers)):
        somme_ponderations = 0
        ponderation_max = 0
        for j in range(0, len(requete.split())):
            somme_ponderations += ponderation_finale[i][j]
            ponderation_max += ponderations[j][-1][1]
        if somme_ponderations <= ponderation_max:
            fichiers_ponderes.append((liste_fichiers[i], 1))
        else:
            fichiers_ponderes.append((liste_fichiers[i], 0))
        # fichiers_ponderes.append((liste_fichiers[i], somme_ponderations))

    outfile = open("result-tf-naif.json", 'w')
    outfile.write(json.dumps(fichiers_ponderes))

    return ponderation_tf_finale


def requete_tf_robertson(requete):
    """
    Fonction requete tf robertson
    """
    index_file = open("index.json", 'r')
    index = json.load(index_file)
    index_reverse_file = open("index-reverse.json", 'r')
    index_reverse = json.load(index_reverse_file)
    ponderations = []
    ponderations_tf = []

    liste_fichiers = []
    for fichier in index_reverse["documents"]:
        liste_fichiers.append(fichier["fichier"])

    for mot_recherche in requete.split():
        fichiers_ordonnes = []
        tf = {}
        ponderations_mot_courant = []
        for mot in index["mots"]:
            if mot["mot"] == mot_recherche:
                fichiers_ordonnes = sorted(mot['fichiers'].items(), key=operator.itemgetter(1), \
                                           reverse=True)

                for value in fichiers_ordonnes:
                    tf[value[0]] = value[1]/(0.5+1.5*(get_nb_de_mots(value[0])/\
                                             index_reverse['nb_mots_moyen'])+value[1])
        if tf != {}:
            fichiers_ordonnes = sorted(tf.items(), key=operator.itemgetter(1), reverse=True)
            for i in range(0, len(fichiers_ordonnes)):
                # fichiers_ordonnes[i][0] : nom du fichier
                # fichiers_ordonnes[i][1] : occurence du mot recherché
                if i == 0:
                    ponderations_mot_courant.append((fichiers_ordonnes[i][0], 1))
                else:
                    if fichiers_ordonnes[i][1] == fichiers_ordonnes[i-1][1]:
                        ponderations_mot_courant.append((fichiers_ordonnes[i][0], \
                                                         ponderations_mot_courant[i-1][1]))
                    else:
                        ponderations_mot_courant.append((fichiers_ordonnes[i][0], \
                                                         ponderations_mot_courant[i-1][1]+1))


        if ponderations_mot_courant == []:
            for i in range(0, len(liste_fichiers)):
                ponderations_mot_courant.append((liste_fichiers[i][0], 0))

        ponderations.append(ponderations_mot_courant)
        ponderations_tf.append(fichiers_ordonnes)

    ponderation_finale = [[(x-x+y-y) for x in range(0, len(requete.split()))] \
                             for y in range(0, len(liste_fichiers))]
    for i in range(0, len(liste_fichiers)):
        for j in range(0, len(requete.split())):
            for k in range(0, len(ponderations[j])):
                if liste_fichiers[i] == ponderations[j][k][0]:
                    ponderation_finale[i][j] = ponderations[j][k][1]
            if ponderation_finale[i][j] == 0:
                ponderation_finale[i][j] = ponderations[j][-1][1]+1

    ponderation_tf_finale = [[(liste_fichiers[y], (x-x)) for x in range(0, len(requete.split()))] \
                                                     for y in range(0, len(liste_fichiers))]
    for i in range(0, len(liste_fichiers)):
        for j in range(0, len(requete.split())):
            for k in range(0, len(ponderations_tf[j])):
                if liste_fichiers[i] == ponderations_tf[j][k][0]:
                    ponderation_tf_finale[i][j] = (ponderations_tf[j][k][0], \
                                                    ponderations_tf[j][k][1])

    fichiers_ponderes = []
    for i in range(0, len(liste_fichiers)):
        somme_ponderations = 0
        ponderation_max = 0
        for j in range(0, len(requete.split())):
            somme_ponderations += ponderation_finale[i][j]
            ponderation_max += ponderations[j][-1][1]
        if somme_ponderations <= ponderation_max:
            fichiers_ponderes.append((liste_fichiers[i], 1))
        else:
            fichiers_ponderes.append((liste_fichiers[i], 0))
        # fichiers_ponderes.append((liste_fichiers[i], somme_ponderations))

    outfile = open("result-tf-robertson.json", 'w')
    outfile.write(json.dumps(fichiers_ponderes))

    return ponderation_tf_finale

def calcul_idf(mot_requete):
    """
    Fonction calcul idf
    """
    index_file = open("index.json", 'r')
    index = json.load(index_file)
    index_reverse_file = open("index-reverse.json", 'r')
    index_reverse = json.load(index_reverse_file)
    for mot in index["mots"]:
        if mot_requete == mot["mot"]:
            return math.log(len(index_reverse["documents"])/len(mot["fichiers"]))
    return 0

def calcul_tfidf(tf, idf):
    """
    Fonction calcul tfidf
    """
    tfidf = {}
    for i in range(0, len(tf)):
        tmp = 0
        for j in range(0, len(idf)):
            tmp += tf[i][j][1]*idf[j]
        tfidf[tf[i][0][0]] = tmp
    return sorted(tfidf.items(), key=operator.itemgetter(1), reverse=True)

def calcul_ps(tfidf, idf):
    """
    Fonction calcul ps
    """
    ps = {}
    for i in range(0, len(tfidf)):
        tmp = 0
        for j in range(0, len(idf)):
            tmp += tfidf[i][1]*idf[j]
        ps[tfidf[i][0]] = tmp
    return sorted(ps.items(), key=operator.itemgetter(1), reverse=True)

def calcul_cd(tfidf, idf):
    """
    Fonction calcul cd
    """
    cd = {}
    for i in range(0, len(tfidf)):
        tmp = 0
        for j in range(0, len(idf)):
            if tfidf[i][1] == 0 or idf[j] == 0:
                tmp = 0
            else:
                tmp += (2*(tfidf[i][1]*idf[j])/((tfidf[i][1]*tfidf[i][1])+(idf[j]*idf[j])))
        cd[tfidf[i][0]] = tmp
    return sorted(cd.items(), key=operator.itemgetter(1), reverse=True)

def calcul_cos(tfidf, idf):
    """
    Fonction calcul cos
    """
    cos = {}
    for i in range(0, len(tfidf)):
        tmp = 0
        for j in range(0, len(idf)):
            if tfidf[i][1] == 0 or idf[j] == 0:
                tmp = 0
            else:
                tmp += ((tfidf[i][1]*idf[j])/(math.sqrt((tfidf[i][1]*tfidf[i][1])+(idf[j]*idf[j]))))
        cos[tfidf[i][0]] = tmp
    return sorted(cos.items(), key=operator.itemgetter(1), reverse=True)

def calcul_jaccard(tfidf, idf):
    """
    Fonction calcul jaccard
    """
    jac = {}
    for i in range(0, len(tfidf)):
        tmp = 0
        for j in range(0, len(idf)):
            if tfidf[i][1] == 0 or idf[j] == 0:
                tmp = 0
            else:
                tmp += ((tfidf[i][1]*idf[j])/((tfidf[i][1]*tfidf[i][1])+(idf[j]*idf[j])-\
                (tfidf[i][1]*idf[j])))
        jac[tfidf[i][0]] = tmp
    return sorted(jac.items(), key=operator.itemgetter(1), reverse=True)

def calcul_rappel_precision(methode):
    """
    Fonction calcul rappel precision
    """
    tableau_a_deux_dimensions = [[(x-x+y-y) for x in range(0, 2)] for y in range(0, 137)]
    for k in range(1, 12):
        fichier_qrel = open("../RessourcesProjet/qrels/qrelQ" + str(k) + ".txt", 'r')
        sep = fichier_qrel.read().split("\n")
        reference = {}
        nb_pertinents = 0
        for i in range(0, len(sep)-1):
            reference[sep[i].split("\t")[0]] = sep[i].split("\t")[1]
            if sep[i].split("\t")[1] == "1":
                nb_pertinents += 1

        result_file = open("resultats/result-q" + str(k) + "-"+methode+".json", 'r')
        fichier_result = json.load(result_file)

        nb_fichiers_pertinents_trouves = 0
        for i in range(0, len(fichier_result)):
            if reference[fichier_result[i][0]] == "1":
                nb_fichiers_pertinents_trouves += 1
            tableau_a_deux_dimensions[i][0] += nb_fichiers_pertinents_trouves/nb_pertinents
            tableau_a_deux_dimensions[i][1] += nb_fichiers_pertinents_trouves/(i+1)

    for i in range(0, len(fichier_result)):
        tableau_a_deux_dimensions[i][0] = tableau_a_deux_dimensions[i][0] / 11
        tableau_a_deux_dimensions[i][1] = tableau_a_deux_dimensions[i][1] / 11
    out_file = open("evaluations/rappel-precision-" + methode + ".csv", 'w')
    out_file.write("Ra, Pr\n")
    for i in range(0, len(tableau_a_deux_dimensions)):
        out_file.write(str(tableau_a_deux_dimensions[i][0]) + ", " + \
        str(tableau_a_deux_dimensions[i][1]) + "\n")

def ask(queryString):
    """
    Execute une requête SPARQL
    """
    sparql = SPARQLWrapper("http://localhost:3030/TP-5A")
    sparql.setQuery(queryString)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results

def strategie_un(requete):
    """
    Fonction strategie un
    """
    mot_requete = requete.split()
    mots_temp = []
    mot_retour = requete
    for i in range(0, len(mot_requete)):
        for j in range(i, len(mot_requete)):
            if i != j:
                if j <= i+1:
                    mots_temp.append(mot_requete[i]+" "+mot_requete[j])
                else:
                    mots_temp.append(mots_temp[-1]+" "+mot_requete[j])
    mot_requete.extend(mots_temp)

    for mot in mot_requete:
        resultats = ask("\
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\
                PREFIX FilmographieV1: <http://www.irit.fr/recherches/MELODI/ontologies/FilmographieV1.owl#>\
                SELECT ?label\
                WHERE {\
                  {?subject rdfs:label \"" + mot + "\"@fr .\
                  ?subject rdfs:label ?label .\
                  FILTER (lang(?label) = 'fr')}\
                  UNION\
                  {?subject rdfs:label \"" + mot + "\".\
                  ?subject rdfs:label ?label}\
                }\
                LIMIT 25\
                ")

        for result in resultats["results"]["bindings"]:
            if result["label"]["value"]+" " not in mot_retour and \
               " "+result["label"]["value"] not in mot_retour:
                mot_retour += " "+result["label"]["value"]
           #print(result["label"]["value"])
    s = mot_retour.lower()
    slist = s.split()
    retour = " ".join(sorted(set(slist), key=slist.index))
    return retour

def strategie_deux(requete):
    """
    Fonction strategie deux
    """
    mot_requete = requete.split()
    mots_temp = []
    mot_retour = requete
    for i in range(0, len(mot_requete)):
        for j in range(i, len(mot_requete)):
            if i != j:
                if j <= i+1:
                    mots_temp.append(mot_requete[i]+" "+mot_requete[j])
                else:
                    mots_temp.append(mots_temp[-1]+" "+mot_requete[j])
    mot_requete.extend(mots_temp)
    for i in range(0, len(mot_requete)):
        for j in range(i, len(mot_requete)):
            resultats = ask("\
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\
                    PREFIX FilmographieV1: <http://www.irit.fr/recherches/MELODI/ontologies/FilmographieV1.owl#>\
                    SELECT ?labelReq\
                    WHERE {\
                        {?uriProp rdfs:label \"" + mot_requete[i] + "\"@fr .\
                        ?uriResTrappes rdfs:label \"" + mot_requete[j] + "\"@fr .\
                        ?uriResTrappes ?uriProp ?uriReq .\
                        ?uriReq rdfs:label ?labelReq}\
                        UNION\
                        {?uriProp rdfs:label \"" + mot_requete[j] + "\"@fr .\
                        ?uriResTrappes rdfs:label \"" + mot_requete[i] + "\"@fr .\
                        ?uriResTrappes ?uriProp ?uriReq .\
                        ?uriReq rdfs:label ?labelReq}\
                        UNION\
                        {?uriProp rdfs:label \"" + mot_requete[i] + "\" .\
                        ?uriResTrappes rdfs:label \"" + mot_requete[j] + "\" .\
                        ?uriResTrappes ?uriProp ?uriReq .\
                        ?uriReq rdfs:label ?labelReq}\
                        UNION\
                        {?uriProp rdfs:label \"" + mot_requete[j] + "\" .\
                        ?uriResTrappes rdfs:label \"" + mot_requete[i] + "\" .\
                        ?uriResTrappes ?uriProp ?uriReq .\
                        ?uriReq rdfs:label ?labelReq}\
                        UNION\
                        {?uriProp rdfs:label \"" + mot_requete[i] + "\".\
                        ?uriResTrappes rdfs:label \"" + mot_requete[j] + "\"@fr .\
                        ?uriResTrappes ?uriProp ?uriReq .\
                        ?uriReq rdfs:label ?labelReq}\
                        UNION\
                        {?uriProp rdfs:label \"" + mot_requete[j] + "\"@fr .\
                        ?uriResTrappes rdfs:label \"" + mot_requete[i] + "\" .\
                        ?uriResTrappes ?uriProp ?uriReq .\
                        ?uriReq rdfs:label ?labelReq}\
                        UNION\
                        {?uriProp rdfs:label \"" + mot_requete[i] + "\"@fr .\
                        ?uriResTrappes rdfs:label \"" + mot_requete[j] + "\" .\
                        ?uriResTrappes ?uriProp ?uriReq .\
                        ?uriReq rdfs:label ?labelReq}\
                        UNION\
                        {?uriProp rdfs:label \"" + mot_requete[j] + "\" .\
                        ?uriResTrappes rdfs:label \"" + mot_requete[i] + "\"@fr .\
                        ?uriResTrappes ?uriProp ?uriReq .\
                        ?uriReq rdfs:label ?labelReq}\
                    }\
                    LIMIT 25\
                    ")
        for result in resultats["results"]["bindings"]:
            if result["labelReq"]["value"] + " " not in mot_retour and " " + \
               result["labelReq"]["value"] not in mot_retour:
                mot_retour += " "+result["labelReq"]["value"]
           #print(result["label"]["value"])
    s = mot_retour.lower()
    slist = s.split()
    retour = " ".join(sorted(set(slist), key=slist.index))
    return retour

if __name__ == "__main__":
    """
    Fonction main
    """
    REQUETE_LISTE = ["personnes Intouchables", "lieu naissance Omar Sy", \
    "personnes récompensées Intouchables", "palmarès Globes de Cristal 2012", \
    "membre jury Globes de Cristal 2012", "prix Omar Sy Globes de Cristal 2012", \
    "lieu Globes Cristal 2012", "prix Omar Sy", "acteur a joué avec Omar Sy", \
    "prix enfant de Trappes", "personne a joué avec Omar Sy"]

    TF = []
    IDF = []
    TFIDF = {}
    REQUETE = ""
    if len(sys.argv) > 1:
        if "-q1" in sys.argv:
            REQUETE = REQUETE_LISTE[0]
        if "-q2" in sys.argv:
            REQUETE = REQUETE_LISTE[1]
        if "-q3" in sys.argv:
            REQUETE = REQUETE_LISTE[2]
        if "-q4" in sys.argv:
            REQUETE = REQUETE_LISTE[3]
        if "-q5" in sys.argv:
            REQUETE = REQUETE_LISTE[4]
        if "-q6" in sys.argv:
            REQUETE = REQUETE_LISTE[5]
        if "-q7" in sys.argv:
            REQUETE = REQUETE_LISTE[6]
        if "-q8" in sys.argv:
            REQUETE = REQUETE_LISTE[7]
        if "-q9" in sys.argv:
            REQUETE = REQUETE_LISTE[8]
        if "-q10" in sys.argv:
            REQUETE = REQUETE_LISTE[9]
        if "-q11" in sys.argv:
            REQUETE = REQUETE_LISTE[10]
        if "-s1" in sys.argv:
            REQUETE = strategie_un(REQUETE)
        if "-s2" in sys.argv:
            REQUETE = strategie_deux(REQUETE)
        if "--generate-index" in sys.argv or "-g" in sys.argv:
            indexer()
        if "--tf-naif" in sys.argv or "-tfn" in sys.argv:
            if REQUETE == "":
                REQUETE = input("[TF-Naïf] Entrez ce que vous cherchez : ")
            print("[TF-Naïf] Calcul du TF-Naïf en cours...")
            TF = requete_tf_naif(REQUETE)
            print("[TF-Naïf] Calcul du TF-Naïf finis")
        if "--tf-robertson" in sys.argv or "-tfr" in sys.argv:
            if REQUETE == "":
                REQUETE = input("[TF-Robertson] Entrez ce que vous cherchez : ")
            print("[TF-Robertson] Calcul du TF-Robertson en cours...")
            TF = requete_tf_robertson(REQUETE)
            print("[TF-Robertson] Calcul du TF-Robertson finis")
        if "-idf" in sys.argv:
            print("[IDF] Calcul de l'IDF en cours...")
            for mot in REQUETE.split():
                IDF.append(calcul_idf(mot))
            print("[IDF] Calcul de l'IDF finis")
            print("[TF.IDF] Calcul de TF.IDF en cours...")
            TFIDF = calcul_tfidf(TF, IDF)
            print("[TF.IDF] Calcul de TF.IDF finis")
        if "-ps" in sys.argv:
            print("[PS] Calcul du PS en cours...")
            RESULTAT = calcul_ps(TFIDF, IDF)
            print("[PS] Calcul du PS finis")
        if "-cd" in sys.argv:
            print("[CD] Calcul du CD en cours...")
            RESULTAT = calcul_cd(TFIDF, IDF)
            print("[CD] Calcul du CD finis")
        if "-cos" in sys.argv:
            print("[COS] Calcul du COS en cours...")
            RESULTAT = calcul_cos(TFIDF, IDF)
            print("[COS] Calcul du COS finis")
        if "-jac" in sys.argv:
            print("[JACCARD] Calcul du JACCARD en cours...")
            RESULTAT = calcul_jaccard(TFIDF, IDF)
            print("[JACCARD] Calcul du JACCARD finis")
        if "-ps" in sys.argv or "-cd" in sys.argv or \
           "-cos" in sys.argv or "-jac" in sys.argv:
            NAME = ""
            for i in range(1, len(sys.argv)):
                NAME += sys.argv[i]
            OUTFILE = open("RESULTATs/result"+NAME+".json", 'w')
            OUTFILE.write(json.dumps(RESULTAT))
        if sys.argv[1] == "tfn-idf-ps" or sys.argv[1] == "tfn-idf-cd" or \
           sys.argv[1] == "tfn-idf-cos" or sys.argv[1] == "tfn-idf-jac" or \
           sys.argv[1] == "tfr-idf-ps" or sys.argv[1] == "tfr-idf-cd" or \
           sys.argv[1] == "tfr-idf-cos" or sys.argv[1] == "tfr-idf-jac" or \
           sys.argv[1] == "s1-tfn-idf-ps" or sys.argv[1] == "s1-tfn-idf-cd" or\
           sys.argv[1] == "s1-tfn-idf-cos" or sys.argv[1] == "s1-tfn-idf-jac" \
           or sys.argv[1] == "s1-tfr-idf-ps" or sys.argv[1] == "s1-tfr-idf-cd"\
           or sys.argv[1] == "s1-tfr-idf-cos" or sys.argv[1] == "s1-tfr-idf-jac"\
           or sys.argv[1] == "s2-tfn-idf-ps" or sys.argv[1] == "s2-tfn-idf-cd"\
           or sys.argv[1] == "s2-tfn-idf-cos" or sys.argv[1] == "s2-tfn-idf-jac"\
           or sys.argv[1] == "s2-tfr-idf-ps" or sys.argv[1] == "s2-tfr-idf-cd" \
           or sys.argv[1] == "s2-tfr-idf-cos" \
           or sys.argv[1] == "s2-tfr-idf-jac":
            calcul_rappel_precision(str(sys.argv[1]))
