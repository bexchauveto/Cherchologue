#!/bin/bash

for i in {1..11}
do
	for j in {1..2}
	do
		./main.py -q${i} -s${j} -tfn -idf -ps
		./main.py -q${i} -s${j} -tfn -idf -cd
		./main.py -q${i} -s${j} -tfn -idf -cos
		./main.py -q${i} -s${j} -tfn -idf -jac
		./main.py -q${i} -s${j} -tfr -idf -ps
		./main.py -q${i} -s${j} -tfr -idf -cd
		./main.py -q${i} -s${j} -tfr -idf -cos
		./main.py -q${i} -s${j} -tfr -idf -jac
	done
done
