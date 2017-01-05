#!/usr/bin/env python3
from pprint import pprint
from SPARQLWrapper import SPARQLWrapper, JSON

def ask(queryString):
    sparql = SPARQLWrapper("http://localhost:3030/TP-5A")
    sparql.setQuery(queryString)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    for result in results["results"]["bindings"]:
        print(result["label"]["value"])
