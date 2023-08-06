#!/usr/bin/env python

import pyhmmer
import sys

alphabet = pyhmmer.easel.Alphabet.amino()

pipeline = pyhmmer.plan7.Pipeline(alphabet, domE=sys.argv[3])

with pyhmmer.easel.SequenceFile(sys.argv[1], digital=True, alphabet=alphabet) as seq_file:
    sequences = list(seq_file)

with pyhmmer.plan7.HMMFile(sys.argv[2]) as hmm_file:
    # all_hits = list(pyhmmer.hmmsearch(hmm_file, sequences, cpus=sys.argv[4]))

    # pipeline.search_hmm(hmm_file, sequences)
