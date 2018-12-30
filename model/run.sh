GPU_DEVICES=`free-gpu -n 1`
export CUDA_VISIBLE_DEVICES=$GPU_DEVICES

[ $# -ge 1 -a "$1" = "--gpu" ] && use_gpu=1 && shift || use_gpu=0

# GPU check
if [ $use_gpu -eq 1 -a "$GPU_DEVICES" = '-1' ]
then
	exit
fi

MODEL_PATH="."
BPE_CODES="$MODEL_PATH/bpe.codes"
BPE_VOCAB="$MODEL_PATH/bpe.vocab"

python3 custom_constraints.py \
    --BPE-codes $BPE_CODES \
    --BPE-vocab $BPE_VOCAB \
| \
(
    if [ $use_gpu -eq 0 ]
    then
        # using CPU
        python3 -m sockeye.translate \
                            -m $MODEL_PATH \
                            --json-input \
                            --beam-size 20 \
                            --beam-prune 20 \
                            --batch-size 10 \
                            --use-cpu
    else
        # using GPU
        python3 -m sockeye.translate \
                            -m $MODEL_PATH \
                            --json-input \
                            --beam-size 20 \
                            --beam-prune 20 \
                            --device-ids 0 \
                            --disable-device-locking
    fi
) 
: '\
| . post.sh'
