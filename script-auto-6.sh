#!/bin/bash

./main.py tfn-idf-ps 12
./main.py tfn-idf-cd 12
./main.py tfn-idf-cos 12
./main.py tfn-idf-jac 12
./main.py tfr-idf-ps 12
./main.py tfr-idf-cd 12
./main.py tfr-idf-cos 12
./main.py tfr-idf-jac 12

for j in {1..2}
do
	./main.py s${j}-tfn-idf-ps 12
	./main.py s${j}-tfn-idf-cd 12
	./main.py s${j}-tfn-idf-cos 12
	./main.py s${j}-tfn-idf-jac 12
	./main.py s${j}-tfr-idf-ps 12
	./main.py s${j}-tfr-idf-cd 12
	./main.py s${j}-tfr-idf-cos 12
	./main.py s${j}-tfr-idf-jac 12
done