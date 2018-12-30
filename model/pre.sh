#!/bin/bash

BPE_CODES="./bpe.codes"
BPE_VOCAB="./bpe.vocab"

echo $- | python3 make_constraints.py \
            --output STDOUT \
            --BPE-codes $BPE_CODES \
            --BPE-vocab $BPE_VOCAB \
            --compute-factor
