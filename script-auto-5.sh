#!/bin/bash

./main.py -q12 -tfn -idf -ps
./main.py -q12 -tfn -idf -cd
./main.py -q12 -tfn -idf -cos
./main.py -q12 -tfn -idf -jac
./main.py -q12 -tfr -idf -ps
./main.py -q12 -tfr -idf -cd
./main.py -q12 -tfr -idf -cos
./main.py -q12 -tfr -idf -jac

for j in {1..2}
do
	./main.py -q12 -s${j} -tfn -idf -ps
	./main.py -q12 -s${j} -tfn -idf -cd
	./main.py -q12 -s${j} -tfn -idf -cos
	./main.py -q12 -s${j} -tfn -idf -jac
	./main.py -q12 -s${j} -tfr -idf -ps
	./main.py -q12 -s${j} -tfr -idf -cd
	./main.py -q12 -s${j} -tfr -idf -cos
	./main.py -q12 -s${j} -tfr -idf -jac
done