#!/usr/bin/env python

import argparse

def get_args():
    parser= argparse.ArgumentParser(description="Removes PCR duplicates from sam file")
    parser.add_argument("-f", help= "filtered SAM file")
    parser.add_argument("-o", help= "final output file")
    return parser.parse_args()
args = get_args()

out = open(args.o, 'w')

with open(args.f, 'r') as fh:
    lines = {}
    for line in fh:
        line = line.strip()
        if line.startswith('@'):
            out.write(line + '\n')
            continue
        splitline = line.split('\t')
        umi = splitline[0].split(':')[-2]
        ogpos = splitline[0].split(':')[-1]
        cigar = splitline[5]
        pos = splitline[3]
        chro = splitline[2]
        flag = splitline[1]
        #Whether strand is forward or reverse from bitwise flag
        if((int(flag) & 16) == 16):
            reverse = True
        else:
            reverse = False
        newqname = splitline[0][:-1]
        newline = [newqname] + splitline[1:3] + [ogpos] + splitline[4:]

        if (chro, pos) not in lines:
            for l in lines:
                for g in lines[l]:
                    out.write(('\t').join(lines[l][g]) + '\n')
            lines = {}
            lines[(chro, pos)] = {(umi, reverse): newline}
        else:
            if (umi, reverse) in lines[(chro, pos)]:
                continue
            else:
                lines[(chro, pos)][(umi, reverse)] = newline
    for l in lines:
        for g in lines[l]:
            out.write(('\t').join(lines[l][g]) + '\n')
    out.close()