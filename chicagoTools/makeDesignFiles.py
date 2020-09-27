'''
WARNING: This code is python2.7! We have to change synatax.

makeDesignFiles.py is used to generate the required files to run CHiCAGO. 
These files contain information on the regions around the baits that have been specified in the .baitmap file.

There are 2 input files to the code: the .rmap file and the .baitmap file.
The code outputs 3 files: .poe file, .npb file, and .nbpb file.
'''

#! /usr/bin/env python
import getopt
import sys
import random
import fnmatch
import os
from collections import Counter

class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def __getattr__(self, attr):
       return getattr(self.stream, attr)

sys.stdout = Unbuffered(sys.stdout)


'''
str2bool(v):
Any input v it converts to lower case and checks its presence in the list given below.
By converting to lower case inputs like Yes are also considered.
'''
def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")


# Default Values for the parameters
minFragLen=-1
maxFragLen=-1
maxLBrownEst = 1.5e6
binsize = 20000
removeB2B=True
removeAdjacent=True
rmapfile = ""
baitmapfile = ""
outfilePrefix = ""
designDir=""


# Prints input format and describes the parameters.
def usage():
  print("Usage: python makeDesignFiles.py --minFragLen=<n> --maxFragLen=<n>  [--maxLBrownEst=%d] [--binsize=%d] [removeb2b=True] [--removeAdjacent=True]\n\t[--rmapfile=<designDir>/*.rmap]\n\t[--baitmapfile=<designDir>/*.baitmap]\n\t[--designDir=.]\n\t[--outfilePrefix]\n\nminFragLen and maxFragLen no longer have defaults to prevent errors. Our recommended values for these parameters are:\n\tHindIII - 150 and 40000;\n\tDpnII - 75 and 1200, respectively\n\nIf designDir is provided and contains a single <baitmapfile>.baitmap and <rmapfile>.rmap, these will be used unless explicitly specified.\nLikewise, the output files will be saved in the designDir unless explicitly specified." % (maxLBrownEst, binsize))


'''
Parameters taken by the python code:

-m [minFragLen value]
-x [maxFragLen value]
-l [maxLBrownEst value]
-b [binsize value]
-B {This does not take a parameter value. If specified, then removeb2b has a boolean value of True}
-j {This does not take a parameter value. If specified, then removeAdjacent has a boolean value of True}
-r [rmapfile path]
-f [baitmapfile path]
-o [outfilePrefix Name]
-d [DesignDir path]

getopt.getopt(sys.argv[1:] Takes all arguments from the commnd line statement used to run this code and labels the inputs 'm:x:l:b:Bjr:f:o:d:'. Example:
m: means the commnd line has the argument `-m 32`, which stands for minFragLen which is given as 32 by the user
B  means the commnd line has the argument `-B`, which stands for removeB2B, it doesn't need an input

The `try-except` statements are used for checking if all arguments are given by the user
'''
try: 
  opts, args = getopt.getopt(sys.argv[1:], 'm:x:l:b:Bjr:f:o:d:', \
['minFragLen=', 'maxFragLen=', 'maxLBrownEst=', 'binsize=', 'removeb2b=', 'removeAdjacent=', 'rmapfile=', 'baitmapfile=', 'outfilePrefix=', 'designDir='])
except getopt.GetoptError:
  usage()
  sys.exit(120)
   
# Assigns each of the input parameters to a variable
for opt, arg in opts: 
  if opt in ('--minFragLen', '-m'):
    minFragLen = long(arg)
  elif opt in ('--maxFragLen', '-x'):
    maxFragLen = long(arg)
  elif opt in ('--maxLBrownEst', '-l'):
    maxLBrownEst = long(arg)
  elif opt in ('--binsize', '-b'):
    binsize = long(arg)
  elif opt == '--removeb2b':
    removeB2B = str2bool(arg)
  elif opt == '--removeAdjacent':
    removeAdjacent = str2bool(arg)
  elif opt == '-B':
    removeB2B = True  
  elif opt == '-j':
    removeAdjacent = True
  elif opt in ('--rmapfile', '-r'):
    rmapfile = arg
  elif opt in ('--baitmapfile', '-f'):
    baitmapfile = arg
  elif opt in ('--outfilePrefix', '-o'):
    outfilePrefix = arg
  elif opt in ('--designDir', '-d'):
    designDir = arg

      
# Error handling till next comment. Checking for existence of files, directories, etc that were given as input.
if minFragLen==-1 or maxFragLen==-1:
   print("--minFragLen and --maxFragLen need to be defined explicitly. Our recommended values for these parameters are:\nHindIII - 150 and 40000 bps;\nDpnII - 75 and 1200 bps, respectively")
   usage()
   sys.exit(1)
   
if designDir != "":
  if os.path.isdir(designDir):
    print("\nUsing designDir %s" % designDir)
  else:
    print("\nError: designDir does not exist.\n")
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
    print("Located baitmapfile %s in %s" % (whichFiles[0], designDir))
  else:
    print("\nError: could not unambiguously locate baitmapfile in designDir.\n")
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
    print("Located rmapfile %s in %s" % (whichFiles[0], designDir))
  else:
    print("\nError: could not unambiguously locate rmapfile in designDir.\n")
    usage()
    sys.exit(1)

if outfilePrefix == "":
  # The common file name for all output files, which will be different by extension
  filename = os.path.splitext(os.path.basename(rmapfile))[0]
  outfilePrefix = os.path.join(designDir,filename)
  
print("Using options:\n\tminFragLen=%d, maxFragLen=%d, maxLBrownEst=%d, binsize=%d, removeb2b=%r, removeAdjacent=%r\n\trmapfile=%s\n\tbaitmapfile=%s\n\toutfilePrefix=%s\n" \
% (minFragLen, maxFragLen, maxLBrownEst, binsize, removeB2B, removeAdjacent, rmapfile, baitmapfile, outfilePrefix))

# Till here. Checked for existence of files, directories, etc that were given as input.


'''
Open the rmap file. It looks like this:
 
20	1	   60024	403460
20	60025	62654	403461
20	62655	66475	403462
20	66476	71941	403463
20	71942	73977	403464

Column 1: describes the chromosome on which the fragment is found.
Column 2: describes the position of the first nucleotide of the fragment.
Column 3: describes the position of the last nucleotide of the fragment.
Column 4: describes the fragment ID.

The following code fragment checks the rmap file for incosistencies and then creates 4 lists for each of the colummns in the rmap file
'''
a = open(rmapfile)
print "Reading rmap...."
chr = []
st = []
end = []
id = []
r_row = set()	         # set() Method creates an iterable containing distinct elements. Can be used on tuples, lists, etc.
for line in a:
  line = line.strip()
  r_row.add(line)
  l = line.split("\t")
  if len(l)!=4:	      # Check number of columns in rmap file.
    print("Error: rmap file should have 4 columns: <chr> <start> <end> <id>. Got %d:" % len(l))
    print(l)
    sys.exit(0)
  chr.append(l[0])      # chr = list of chromosome numbers.
  st.append(int(l[1]))	# st = list of starting restriction cut sites.
  end.append(int(l[2]))	# end = list of ending restriction cut sites.
  id.append(int(l[3]))	# id = list of IDs given to restriction fragments.
a.close()


'''
How Counter() works:

a = ['apple', 'ball', 'apple', 'cat']
Counter(a).items()

Output:
['apple',2]
['ball',1]
['cat',1]

Checks list of rmap IDs for duplicates
'''
if len(set(id)) != len(id):
  z = [k for k,v in Counter(id).items() if v>1]  # k = ID, v = Count of the ID in the list "id"
  print("Error: duplicate IDs found in rmap:")
  print(z)  	 # List of IDs which have duplicates in the list "id".
  print("Exiting...\n")
  sys.exit(1)


'''
Open the rmap file. It looks like this:
 
20	66476	   71941	   403463	DEFB125
20	119103	138049	403475	DEFB126
20	161620	170741	403482	DEFB128
20	206075	209203	403491	DEFB129
20	233983	239479	403499	DEFB132

Column 1: the chromosome on which the bait fragment is found.
Column 2: the position of the first nucleotide of the bait fragment.
Column 3: the position of the last nucleotide of the bait fragment.
Column 4: the fragment ID corresponding to the .rmap file.
Column 5: the bait ID.

The following code fragment checks the rmap file for incosistencies and then creates a list of bait IDs
It also ensures that baitmap is a subset of rmap.
'''
b = open(baitmapfile)
print("Reading baitmap...")
bid = []
for line in b:
  line = line.strip()
  l = line.split("\t")
  if len(l)!=5:
    print("Error: baitmap file should have 5 columns: <chr> <start> <end> <id> <annotation>. Got %d:" % len(l))
    print(l)
    sys.exit(1)
  if "\t".join(l[0:4]) not in r_row:
    print("Error - the following entry in baitmapfile is not found in rmap:")	# Ensures that baitmap is a subset of rmap. rmap is the superset.
    print(l[0:4])
    print("Exiting...\n")
    sys.exit(1)
  bid.append(int(l[3]))	                # bid = list of bait IDs.
b.close()

# r_row was the set of unique lines in the rmap file
del r_row

bid0 = bid
bid = set(bid)   # typecasts "bid" as a set() 


# Checks list of baitmap IDs for duplicates
if len(bid) != len(bid0):
  z = [k for k,v in Counter(bid0).items() if v>1]
  print("Error: duplicate IDs found in baitmap:")
  print(z)
  print("Exiting...\n")
  sys.exit(1)

# delete original list of bait IDs. bait IDs now present in bid, which is a set() object
del bid0

print("Sorting rmap...")

'''
How zip() works?

a = ['a','b','c']
b = [1, 2, 3]
zip(a,b)

Output:
zipobject
{('a',1),('b',2),('c',3)}

Sorting the rmap lists in the order chromosome #, start position, end position, ID
zip ensures that while sorting, there is no mixing of the chromosome #, start position, end position, ID
'''
oldchr = chr
oldst = st
chr = [x for (x,y) in sorted(zip(oldchr, oldst))]	
st = [y for (x,y) in sorted(zip(oldchr, oldst))]
end = [z for (x,y,z) in sorted(zip(oldchr, oldst, end))]
id = [z for (x,y,z) in sorted(zip(oldchr, oldst, id))]
del oldchr
del oldst


### make NPerBinFile

# Open .npb file and write header which contains the paramerter values
npbfile = outfilePrefix+".npb"
npb = open(npbfile, "wt")
npb.write("#\tminFragLen=%d\tmaxFragLen=%d\tmaxLBrownEst=%d\tbinsize=%d\tremoveb2b=%r\tremoveAdjacent=%r\trmapfile=%s\tbaitmapfile=%s\n" % \
(minFragLen, maxFragLen, maxLBrownEst, binsize, removeB2B, removeAdjacent, rmapfile, baitmapfile))

# Open .poe file and write header which contains the paramerter values
poefile = outfilePrefix+".poe"
poe = open(poefile, "wt")
poe.write("#\tminFragLen=%d\tmaxFragLen=%d\tmaxLBrownEst=%d\tbinsize=%d\tremoveb2b=%r\tremoveAdjacent=%r\trmapfile=%s\tbaitmapfile=%s\n" % \
(minFragLen, maxFragLen, maxLBrownEst, binsize, removeB2B, removeAdjacent, rmapfile, baitmapfile))

print("\nCreating .npb and .poe files...")

print("Looping through baits...")


# Iterates over the start positions of the baits
for i in range(len(st)):
  
  # If ID not in set of bait IDs, then skip 
  if not id[i] in bid:
    continue
  
  # n is a list with its elements representing the bin counts. len(n) = number of bins.
  n = [0]*int(round(float(maxLBrownEst)/binsize)) 

  '''
  Iterates over the fragments which are before fragment i. Hence it iterates over fragment i-1 to 1.
  After it has reached a fragment such that d >= maxLBrownEst, then it breaks away from the loop.
  If it reaches a fragment which is on another chromosome, it breaks away from the loop. 
  '''
  for j in range(i-1,0,-1):
   if chr[j] != chr[i]:
     break
   if removeB2B:
     if id[j] in bid:
       continue 
   if removeAdjacent:
     if j==i-1:
       continue
   if (end[j]-st[j])<minFragLen:
     continue
   if (end[j]-st[j])>maxFragLen:
     continue       
   d = (st[i]+end[i])/2-(st[j]+end[j])/2	#Distance between the midpoints of fragment i and fragment j.
   if d>=maxLBrownEst:
     break
   n[d/binsize] += 1	#typeset to int()
   poe.write("%d\t%d\t%d\n" % (id[i], id[j], d))  


  '''
  Iterates over the fragments which are before fragment i. Hence it iterates over fragment i+1 to end of the list (list contains fragments from all chromosomes).
  After it has reached a fragment such that d >= maxLBrownEst, then it breaks away from the loop.
  When it reaches a fragment which is on another chromosome, it breaks away from the loop. 
  '''
  for j in range(i+1,len(st),1):
   if chr[j] != chr[i]:
     break
   if removeB2B:
     if id[j] in bid:
       continue
   if removeAdjacent:
     if j==i+1:
       continue 
   if (end[j]-st[j])<minFragLen:
     continue
   if (end[j]-st[j])>maxFragLen:
     continue       
   
   d = (st[j]+end[j])/2-(st[i]+end[i])/2
   if d>=maxLBrownEst:
     break
   n[d/binsize] += 1
   poe.write("%d\t%d\t%d\n" % (id[i], id[j], d))  
  
  '''
  The direction of the fragment j with respect to fragment i does not matter while binning.
  If fragment j1 and j2 are almost at the same distance from fragment i but on different sides of i, they will still be in the same bin.
  Hence first value in list 'n' denotes no. of fragments found in the closest bin.
  '''  
  npb.write("%d\t" % id[i])
  for k in range(len(n)):
    npb.write("%d" % n[k])
    if k!=len(n)-1:
      npb.write("\t")
  npb.write("\n")
  
  #Just to show progress in for loop.
  if int(random.uniform(0,100))==1: 
   print("%d " % i,)

npb.close()
poe.close()

### make NBaitsPerBinFile

'''
Does the exact same thing as above but only for Bait2Bait map.
Be a good coder and write a function for this.
'''
print "\nCreating .nbpb file - this will take a while..."

print "Looping through other ends..."

outfile = outfilePrefix+".nbpb"
of = open(outfile, "wt")
of.write("#\tmaxLBrownEst=%d\tbinsize=%d\trmapfile=%s\tbaitmapfile=%s\n" % (maxLBrownEst, binsize, rmapfile, baitmapfile))

for i in range(len(st)):
    
  n = [0]*int(round(float(maxLBrownEst)/binsize))
  
  if removeAdjacent:
    iSt=i-2
  else:
    iSt=i-1

  for j in range(iSt,0,-1):
   if chr[j] != chr[i]:
    break
   d = (st[i]+end[i])/2-(st[j]+end[j])/2
   if d>=maxLBrownEst:
    break
   if id[j] in bid:
    n[d/binsize] += 1
  
  if removeAdjacent:
    iSt=i+2
  else:
    iSt=i+1

  for j in range(iSt,len(st),1):
   if chr[j] != chr[i]:
    break
   d = (st[j]+end[j])/2-(st[i]+end[i])/2
   if d>=maxLBrownEst:
    break
   if id[j] in bid:
    n[d/binsize] += 1
  
  of.write("%d\t" % id[i])
  for k in range(len(n)):
    of.write("%d" % n[k])
    if k!=len(n)-1:
      of.write("\t")
  of.write("\n")
 
  if int(random.uniform(0,1000))==1: 
   print("%d " % i,)

of.close()

prin("\nAll done!")
