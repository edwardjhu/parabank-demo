#!/bin/bash

SCRIPT_PATH=/home/edwardhu/export/paraBank/parabank/scripts/paraphrase_sampler

cat $"-" > .decoded.$1.tmp

python3 $SCRIPT_PATH/to_tsv.py \
	-d .decoded.$1.tmp \
	-r .source.$1.tmp \
	-o STDOUT \
    --diversity 0.65 \
    --output-one
