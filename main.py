#!/usr/bin/env python3
import os

if __name__ == "__main__":
    print("Veuillez entrer le chemin vers le dossier dans lequel vous souhaitez effectuer une recherche :")
    chemin = input()
    for nom_fichier in os.listdir(chemin):
            print("|-" + nom_fichier)
