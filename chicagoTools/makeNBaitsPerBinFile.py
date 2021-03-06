#! /usr/bin/env python
import getopt
import sys
import random
import fnmatch
import os
from ntpath import basename

class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def __getattr__(self, attr):
       return getattr(self.stream, attr)

sys.stdout = Unbuffered(sys.stdout)

maxLBrownEst = 1.5e6
binsize = 20000
rmapfile = ""
baitmapfile = ""
outfile = ""
designDir=""
removeAdjacent = True

def usage():
  print "Usage: python makeNBaitsPerBinFile.py [--maxLBrownEst=%d] [--binsize=%d] [--removeAdjacent=True]\n\t[--rmapfile=designDir/*.rmap]\n\t[--baitmapfile=designDir/*.baitmap]\n\t[--outfile=designDir/<rmapfileName>.nbpb]\n\t[--designDir=.]\n\nIf designDir is provided and contains a single <baitmapfile>.baitmap and <rmapfile>.rmap, these will be used unless explicitly specified.\nLikewise, the output file will be saved as designDir/nbaitsperbin.nbpb unless explicitly specified." \
  % (maxLBrownEst, binsize)

try:
  # minFragLen, maxFragLen and removeb2b aren't used here but included and will be ignored quetly, 
  # so equal command lines can be accepted by all three design scripts
  opts, args = getopt.getopt(sys.argv[1:], 'm:x:l:b:rja:b:f:t:o:d:', \
['minFragLen=', 'maxFragLen=', 'maxLBrownEst=', 'binsize=', \
'removeb2b=', 'removeAdjacent=', 'rmapfile=', 'baitmapfile=', 'outfile=', 'designDir='])

except getopt.GetoptError:
  usage()
  sys.exit(120)
   
for opt, arg in opts: 
  if opt in ('--maxLBrownEst', '-l'):
    maxLBrownEst = long(arg)
  elif opt in ('--binsize', '-b'):
    binsize = long(arg)
  elif opt in ('--rmapfile', '-f'):
    rmapfile = arg
  elif opt in ('--baitmapfile', '-t'):
    baitmapfile = arg
  elif opt in ('--outfile', '-o'):
    outfile = arg
  elif opt in ('--designDir', '-d'):
    designDir = arg
  elif opt == '--removeAdjacent':
    removeAdjacent = str2bool(arg)
  elif opt == '-j':
    removeAdjacent = True
  elif opt in ('--minFragLen', '-m', '--maxFragLen', '-x', '--removeb2b', '-b'):
    pass # options not used by this script
    

if designDir != "":
  if os.path.isdir(designDir):
    print "\nUsing designDir %s" % designDir;
  else:
    print "\nError: designDir does not exist.\n";
    usage()
    sys.exit(1)
else:
  designDir = "."

if baitmapfile == "":
  files = os.listdir(designDir)
  whichFiles = []
  for file in files:
    if fnmatch.fnmatch(file, '*.baitmap'):
        whichFiles.append(file)
  if len(whichFiles)==1:
    baitmapfile=os.path.join(designDir, whichFiles[0])
    print "Located baitmapfile %s in %s" % (whichFiles[0], designDir)
  else:
    print "\nError: could not unambiguously locate baitmapfile in designDir.\n"
    usage()
    sys.exit(1)

if rmapfile == "":
  files = os.listdir(designDir)
  whichFiles = []
  for file in files:
    if fnmatch.fnmatch(file, '*.rmap'):
        whichFiles.append(file)
  if len(whichFiles)==1:
    rmapfile=os.path.join(designDir, whichFiles[0])
    print "Located rmapfile %s in %s" % (whichFiles[0], designDir)
  else:
    print "\nError: could not unambiguously locate baitmapfile in designDir.\n"
    usage()
    sys.exit(1)


if outfile == "":
  rmapfileName = os.path.splitext(basename(rmapfile))[0]
  outfile = os.path.join(designDir, rmapfileName + ".nbpb")
  print "Output fill be saved as %s\n" % outfile

print "Using options:\nmaxLBrownEst=%d, binsize=%d removeAdjacent=%r\n\trmapfile=%s\n\tbaitmapfile=%s\n\toutfile=%s\n" \
% (maxLBrownEst, binsize, removeAdjacent, rmapfile, baitmapfile, outfile)

a = open(rmapfile)
print "Reading rmap...."
chr = []
st = []
end = []
id = []
for line in a:
  line = line.strip()
  l = line.split("\t")
  chr.append(l[0])
  st.append(int(l[1]))
  end.append(int(l[2]))
  id.append(int(l[3]))
a.close()

b = open(baitmapfile)
print "Reading baitmap..."
bid = []
for line in b:
  line = line.strip()
  l = line.split("\t")
  bid.append(int(l[3]))
b.close()

bid = set(bid)

print "Sorting rmap..."

oldchr = chr
oldst = st
chr = [x for (x,y) in sorted(zip(oldchr, oldst))]
st = [y for (x,y) in sorted(zip(oldchr, oldst))]
end = [z for (x,y,z) in sorted(zip(oldchr, oldst, end))]
id = [z for (x,y,z) in sorted(zip(oldchr, oldst, id))]
del oldchr
del oldst

print "Looping through other ends..."

of = open(outfile, "wt")
of.write("#\tmaxLBrownEst=%d\tbinsize=%d\trmapfile=%s\tbaitmapfile=%s\n" % (maxLBrownEst, binsize, rmapfile, baitmapfile))

for i in xrange(len(st)):
    
  n = [0]*int(maxLBrownEst/binsize)
  
  if removeAdjacent:
    iSt=i-2
  else:
    iSt=i-1

  for j in xrange(iSt,0,-1):
   if chr[j] != chr[i]:
    break
   d = st[i]+(end[i]-st[i])/2-(st[j]+(end[j]-st[j])/2)
   if d>=maxLBrownEst:
    break
   if id[j] in bid:
    n[d/binsize] += 1
  
  if removeAdjacent:
    iSt=i+2
  else:
    iSt=i+1

  for j in xrange(iSt,len(st),1):
   if chr[j] != chr[i]:
    break
   d = st[j]+(end[j]-st[j])/2-(st[i]+(end[i]-st[i])/2)
   if d>=maxLBrownEst:
    break
   if id[j] in bid:
    n[d/binsize] += 1
  
  of.write("%d\t" % id[i])
  for k in xrange(len(n)):
    of.write("%d" % n[k])
    if k!=len(n)-1:
      of.write("\t")
  of.write("\n")
 
  if int(random.uniform(0,1000))==1: 
   print "%d " % i,

of.close()

print "Done!"
