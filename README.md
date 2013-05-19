myfirstqapsolver
================

Simple python QAP minimiser made to test out QAP problems listed in
http://www.cs.amherst.edu/ccm/cf14-mcgeoch.pdf

# Single-process sequential run with a 20 second time limit each:
dir=output20
mkdir $dir
for x in `ls QAPproblems`; do
  python qap.py QAPproblems/$x 20 > $dir/${x/.dat/.out}
done
grep ^Best $dir/*

# To run on multiple cores with a 20 second time limit per process:
ls QAPproblems > list
dir=output20
mkdir $dir
./schedule.py -p "$dir 20" ./runscript list
grep ^Best $dir/*
