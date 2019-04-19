# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not
# use this file except in compliance with the License. A copy of the License
# is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

"""
Translation CLI.
"""
import sys
import time
from contextlib import ExitStack
from math import ceil
from typing import Generator, Optional, List

from sockeye.lexicon import TopKLexicon
from sockeye.output_handler import get_output_handler, OutputHandler
from sockeye.utils import determine_context, log_basic_info, check_condition, grouper
from sockeye import arguments
from sockeye import constants as C
from sockeye import data_io
from sockeye import inference
from sockeye import utils

def load_translate(model_path):

    # Seed randomly unless a seed has been passed
    utils.seed_rngs(int(time.time()))

    output_handler = get_output_handler('json',
                                        None,
                                        0.9)

    with ExitStack() as exit_stack:
        context = determine_context(device_ids=[-1],
                                    use_cpu=True,
                                    disable_device_locking=False,
                                    lock_dir=None,
                                    exit_stack=exit_stack)[0]

        models, source_vocabs, target_vocab = inference.load_models(
            context=context,
            max_input_len=None,
            beam_size=20,
            batch_size=1,
            model_folders=[model_path],
            checkpoints=None,
            softmax_temperature=None,
            max_output_length_num_stds=C.DEFAULT_NUM_STD_MAX_OUTPUT_LENGTH,
            decoder_return_logit_inputs=False,
            cache_output_layer_w_b=False,
            override_dtype=None,
            output_scores=output_handler.reports_score(),
            sampling=None)
        store_beam = False
        
        translator = inference.Translator(context=context,
                                          ensemble_mode='linear',
                                          bucket_source_width=10,
                                          length_penalty=inference.LengthPenalty(1.0, 0.0),
                                          beam_prune=30,
                                          beam_search_stop=C.BEAM_SEARCH_STOP_ALL,
                                          nbest_size=10,
                                          models=models,
                                          source_vocabs=source_vocabs,
                                          target_vocab=target_vocab,
                                          restrict_lexicon=None,
                                          avoid_list=None,
                                          store_beam=store_beam,
                                          strip_unknown_words=False,
                                          skip_topk=False,
                                          sample=None)
    return translator

sent_id = 0
def make_input(input_line: Optional[str]):
    global sent_id
    sent_id += 1
    #print('sent_id:', sent_id)
    return inference.make_input_from_json_string(sentence_id=sent_id, json_string=input_line)
    
def read_and_translate(translator: inference.Translator,
                       input_line,
                       nbest_size):
    #for chunk in grouper(make_input(input_line), size=C.CHUNK_SIZE_NO_BATCHING):
    return translate([make_input(input_line)], translator, nbest_size)
    
def translate(trans_inputs: List[inference.TranslatorInput],
              translator: inference.Translator,
              nbest_size: int) -> str:
    #print(trans_inputs)
    trans_outputs = translator.translate(trans_inputs)
    return [trans_outputs[0].nbest_translations[i] for i in range(nbest_size)]

