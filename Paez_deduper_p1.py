#!/usr/bin/env python

import argparse

CIGAR_lets = ['S', 'M', 'I', 'D', 'N']

def get_args():
    parser = argparse.ArgumentParser(description="Filters SAM file by UMI's")
    parser.add_argument("-f", help= "SAM file")
    parser.add_argument("-umi", help= "UMI file")
    parser.add_argument("-o", help= "output file")
    parser.add_argument("-p", help="paired end data? yes or no" )
    return parser.parse_args()

def fix_softclip(CIGAR, POS, FLAG):
    '''Given a CIGAR string, start POS, and bitwise FLAG, this function will 
    parse through the CIGAR string and adjust the POS accordingly, depending on the
    FLAG.'''
    POS = int(POS)

    #Whether strand is forward or reverse from bitwise flag
    if((int(flag) & 16) == 16):
        reverse = True
    else:
        reverse = False

    #forward strand:
    if reverse == False:
        if CIGAR[-1] == 'S':
            CIGAR = CIGAR[:-1]
        if 'S' in CIGAR:
            CIGAR = CIGAR.split('S')[0]
            newpos = POS - int(CIGAR)
        else:
            newpos = POS

    #reverse strand:
    else:
        cigarlet = []
        for let in CIGAR:
            #CIGAR = 3S60M2I5M5S
            if let in CIGAR_lets:
                cigarlet.append(let)
            #cigarlet example list cigarlet = ['S', 'M', 'I', 'M', 'S']

        cigar_list = []
        for let in cigarlet:
            cigarsplitobj = CIGAR.split(let, 1)
            cigar_list.append((cigarsplitobj[0], let))
            CIGAR = cigarsplitobj[1]
            #cigar_list = [(3, 'S'), (6, 'M'), (2, 'I'), (5, 'M'), (5, 'S')]

        #Adjust start POS to include M, N, D, and S-at the end
        newpos = POS
        #If beginning not softclipped and no insertions, increment by #s in CIGAR
        if cigar_list[0][1] != 'S':
            for i in cigar_list:
                if i[1] != 'I':
                    newpos += int(i[0])
        else:
            for i in cigar_list[1:]:
                if i[1] != 'I':
                    newpos += int(i[0])
    return (POS, newpos)

#Filtering SAM file by making UMI dictionary for lines that have appropriate UMIs
args = get_args()
umi_di = {}
#No support for paired-end data
if args.p == 'yes':
    raise Exception("No support for paired-end data yet, sorry.")
    
with open(args.umi) as u:
    for line in u:
        line = line.strip()
        umi_di[line] = []

out = open(args.o, 'w')

#Grabbing CIGAR, FLAG, and POS from line using .split() function
with open(args.f, 'r') as fh:
    for line in fh:
        line = line.strip()
        if line.startswith('@'):
            out.write(line + '\n')
            continue
        splitline = line.split('\t')
        cigar = str(splitline[5])
        flag = splitline[1]
        if((int(flag) & 16) == 16):
            reverse = True
        else:
            reverse = False
        pos = splitline[3]

        splitline[3] = str(fix_softclip(cigar, pos, flag)[1])


        #adding original pos to the end of QNAME
        splitline[0] = splitline[0] + ':' + str(fix_softclip(cigar, pos, flag)[0])

        #sanity check timE!
        # print(pos)
        # print(f'reverse = {reverse}')
        # print(cigar)
        # print(fix_softclip(cigar, pos, flag)[1])
        # print()

        #creating new line with updated position
        line = ('\t').join(splitline)

        for umi in umi_di:
            #Writing new UMI filtered SAM file
            if umi in line.split('\t')[0]:
                out.write(line + '\n')
