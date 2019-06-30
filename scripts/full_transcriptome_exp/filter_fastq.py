#!/usr/bin/env python

import argparse
import sys


'''
    Below code taken from https://github.com/lh3/readfq/blob/master/readfq.py
'''

def readfq(fp): # this is a generator function
    last = None # this is a buffer keeping the last unprocessed line
    while True: # mimic closure; is it a bad idea?
        if not last: # the first record or a record following a fastq
            for l in fp: # search for the start of the next record
                if l[0] in '>@': # fasta/q header line
                    last = l[:-1] # save this line
                    break
        if not last: break
        name, seqs, last = last[1:].replace(" ", "_"), [], None
        for l in fp: # read the sequence
            if l[0] in '@+>':
                last = l[:-1]
                break
            seqs.append(l[:-1])
        if not last or last[0] != '+': # this is a fasta record
            yield name, (''.join(seqs), None) # yield a fasta record
            if not last: break
        else: # this is a fastq record
            seq, leng, seqs = ''.join(seqs), 0, []
            for l in fp: # read the quality
                seqs.append(l[:-1])
                leng += len(l) - 1
                if leng >= len(seq): # have read enough quality
                    last = None
                    yield name, (seq, ''.join(seqs)); # yield a fastq record
                    break
            if last: # reach EOF before reading enough quality
                yield name, (seq, None) # yield a fasta record instead
                break


def main(fastq_file, max_size):
    outpath = fastq_file+'_filtered.fq'
    outfile = open(outpath,'w')
    # reads = readfq(open(fastq_file, 'r'))
    for acc, (seq,qual) in readfq(open(fastq_file, 'r')):
        if len(seq) < max_size:
            outfile.write("@{0}\n{1}\n{2}\n{3}\n".format(acc,seq,"+",qual))
            # print >> outfile, ">{0}\n{1}".format(acc,seq)




if __name__ == '__main__':

    parser = argparse.ArgumentParser("Parses a fasta file and output all sequences longer than min_size to fasta format to /path/to/fasta_file_filtered.fa.")
    parser.add_argument('fasta', type=str, help='Fasta file. ')
    parser.add_argument('max_size', type=int, help='Min size of reads.')

    args = parser.parse_args()

    main(args.fasta, args.max_size)