#!/usr/bin/python
# Scheduler: distributes a job queue amongst 'n' processes
# Usage: schedule.py [options] RUNSCRIPT JOBLIST
# Each line in the file JOBLIST gets passed as an argument to the script RUNSCRIPT
# If -p <params> is used then RUNSCRIPT also gets passed the constant argument <params>
# If -s <startscript> is used then startscript runs first (getting the argument <params> if present)
# -u means run in unbuffered mode. This means that child processes write to stdout and stderr
#    of the parent process (this program, schedule.py) asynchronously, and so stuff can be
#    mangled or lost. This mode could be useful if {there is an unlimited amount of output
#    or if you care about fast feedback} and you don't mind some errors.
#
# Keyboard Interrupt issue due to bug in python (2.6.6 et al)
# http://bugs.python.org/issue8296
# Partial workaround:
# http://stackoverflow.com/questions/1408356/keyboard-interrupts-with-pythons-multiprocessing-pool/
# Non-helpful workaround:
# http://noswap.com/blog/python-multiprocessing-keyboardinterrupt/
#
# Strange default allocation policy
# http://stackoverflow.com/questions/10348156/python-multiprocessing-pool-allocation

import optparse,multiprocessing,subprocess,datetime,sys
from optparse import OptionParser

parser = OptionParser(usage="usage: %prog [options] RUNSCRIPT JOBLIST")
parser.add_option("-?","--wtf",action="help",help="Show this help message and exit")
parser.add_option("-s","--start",dest="start",help="Start script (default: none)")
parser.add_option("-n","--ncpus",dest="ncpus",help="Number of cpus to schedule to (default: all)")
parser.add_option("-p","--params",dest="params",help="Parameter(s) to pass to runscript (and start script, if it exists)")
parser.add_option("-u","--unbuffer",dest="unbuffer",default=False,action="store_true",help="In unbuffered mode, processes simultaneously write to stdout and stderr of parent process, resulting in faster feedback but the possibility of some lines getting lost or mangled (default: off)")

(options,args)=parser.parse_args()
unbuffer=options.unbuffer
start=options.start
ncpus=options.ncpus
if ncpus==None: ncpus=multiprocessing.cpu_count()
else: ncpus=int(ncpus)
params=options.params
if params==None: params=""
else: params=" "+params
if len(args)!=2: parser.error("Expected two arguments")
runscript=args[0]
joblistfn=args[1]
l=multiprocessing.Lock()

def work(job):
  l.acquire();print datetime.datetime.now(),"STARTING",job;sys.stdout.flush();l.release()
  if unbuffer:
    subprocess.call("%s %s%s"%(runscript,job,params),shell=True)
  else:
    p=subprocess.Popen("%s %s%s"%(runscript,job,params),stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    (out,err)=p.communicate()
    l.acquire();sys.stdout.write(out);sys.stderr.write(err);l.release()
  l.acquire();print datetime.datetime.now(),"ENDING",job;
  sys.stdout.flush();sys.stderr.flush();l.release()

if __name__ == '__main__':
  if start: subprocess.call("%s%s"%(start,params),shell=True)
  pool=multiprocessing.Pool(ncpus)
  f=open(joblistfn,'r');jobs=f.read().split('\n')[:-1];f.close()
  pool.map_async(work,jobs).get(10000000000)
