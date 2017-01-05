#!/bin/bash

for i in {1..11}
do
	./main.py -q${i} -tfn -idf -ps
	./main.py -q${i} -tfn -idf -cd
	./main.py -q${i} -tfn -idf -cos
	./main.py -q${i} -tfn -idf -jac
	./main.py -q${i} -tfr -idf -ps
	./main.py -q${i} -tfr -idf -cd
	./main.py -q${i} -tfr -idf -cos
	./main.py -q${i} -tfr -idf -jac
done

