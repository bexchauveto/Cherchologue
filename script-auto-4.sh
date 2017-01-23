#!/bin/bash

for j in {1..2}
do
  ./main.py s${j}-tfn-idf-ps
  ./main.py s${j}-tfn-idf-cd
  ./main.py s${j}-tfn-idf-cos
  ./main.py s${j}-tfn-idf-jac
  ./main.py s${j}-tfr-idf-ps
  ./main.py s${j}-tfr-idf-cd
  ./main.py s${j}-tfr-idf-cos
  ./main.py s${j}-tfr-idf-jac
done
