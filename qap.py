#!/usr/bin/python

# My First QAP Solver
# Reads a QAP file in format given here
# http://www.seas.upenn.edu/qaplib/inst.html
# and tries to find best permutation within given time limit
#
# Usage: qap.py [problem_definition_filename [max_time]]

import sys

if len(sys.argv)>1: f=open(sys.argv[1],'r')
else: f=sys.stdin
if len(sys.argv)>2: maxt=float(sys.argv[2])
else: maxt=1800
n=int(f.readline().strip())
print "n =",n

# Read in problem definition file
i=0;m=[]
for x in f:
  y=x.strip()
  if y=='': continue
  for z in y.split():
    if i%n==0: m.append([])
    m[-1].append(int(z))
    i+=1
assert i==2*n*n
a=m[:n];b=m[n:]

# Objective function
def val(p):
  t=0
  for i in range(n):
    for j in range(n):
      t+=a[i][j]*b[p[i]][p[j]]
  return t

# Change in objective function due to a transposition
def valtrans(p,i,j):
  t=0
  for k in range(n):
    if k!=i and k!=j: t+=(a[k][i]-a[k][j])*(b[p[k]][p[j]]-b[p[k]][p[i]])+\
          (a[i][k]-a[j][k])*(b[p[j]][p[k]]-b[p[i]][p[k]])
  t+=(a[i][i]-a[j][j])*(b[p[j]][p[j]]-b[p[i]][p[i]])
  t+=(a[i][j]-a[j][i])*(b[p[j]][p[i]]-b[p[i]][p[j]])
  return t

import time
from random import randrange
bv=1e90;nn=0;nm=5;mm=[[1e100,0]]*nm;t0=0
l=[]
for i in range(n-1):
  for j in range(i+1,n): l.append((i,j))
N=len(l)
for i in range(N-1): j=i+randrange(N-i);t=l[i];l[i]=l[j];l[j]=t
p=range(n)
while time.clock()<maxt:
  # Start with a random permutation
  for i in range(n-1): j=i+randrange(n-i);t=p[i];p[i]=p[j];p[j]=t
  cv=val(p)
  r=0
  while r<n*(n-1)/2:# Try transpositions until no more benefit
    for (i,j) in l:
      dv=valtrans(p,i,j)
      if dv<0: t=p[i];p[i]=p[j];p[j]=t;cv+=dv;r=0
      else:
        r+=1
        if r==n*(n-1)/2: break
  nn+=1
  if cv<bv: bv=cv
  i=0# Record best nm results
  while i<len(mm) and cv>mm[i][0]: i+=1
  if i<len(mm):
    if cv==mm[i][0]: mm[i][1]+=1
    else: mm=mm[:i]+[[cv,1]]+mm[i:-1]
  tt=time.clock()
  if tt>t0: print "%20s %10.2f %8d %12d"%(sys.argv[1],tt,nn,bv),mm;t0=tt+5;sys.stdout.flush()
print "Best %20s %10.2f %12d"%(sys.argv[1],time.clock(),bv)
