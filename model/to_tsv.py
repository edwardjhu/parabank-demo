import csv
import pdb
import json
import string
from mosestokenizer import MosesDetokenizer
from nltk.translate.bleu_score import SmoothingFunction
from nltk.translate.bleu_score import sentence_bleu, brevity_penalty
from random import choice

system_num = 34

detokenizer = MosesDetokenizer('en')
smoother = SmoothingFunction().method1

def fixTokenization(candidate):
    candidate = candidate.replace("do n't", "don't")
    candidate = candidate.replace("does n't", "doesn't")
    candidate = candidate.replace("did n't", "didn't")
    candidate = candidate.replace("is n't", "isn't")
    candidate = candidate.replace("are n't", "aren't")
    candidate = candidate.replace("was n't", "wasn't")
    candidate = candidate.replace("were n't", "weren't")
    candidate = candidate.replace("ca n't", "can't")
    candidate = candidate.replace("wo n't", "won't")
    candidate = candidate.replace("would n't", "wouldn't")
    candidate = candidate.replace("could n't", "couldn't")
    candidate = candidate.replace("must n't", "mustn't")
    candidate = candidate.replace("need n't", "needn't")
    candidate = candidate.replace('wan na', 'wanna')
    candidate = candidate.replace('gon na', 'gonna')
    candidate = candidate.replace('got ta', 'gotta')
    return candidate

translator = str.maketrans('', '', string.punctuation)
def calcIntersectionUnion(sent_A, sent_B):
    sent_A = sent_A.lower().translate(translator)
    sent_B = sent_B.lower().translate(translator)
    set_A = set(sent_A.split())
    set_B = set(sent_B.split())
    return len(set_A.intersection(set_B))/len(set_A.union(set_B))

if __name__ == '__main__':
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    parser = ArgumentParser(
        description='Get the JSON file for decoding.',
        formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--decoded-path', help='Path to the sockeye output.')
    parser.add_argument('-r', '--ref-path', help='Path to the reference sentence file.')
    parser.add_argument('-o', '--output', help='Path to tsv output.')
    parser.add_argument('--diversity', type=float, default=1.0, help='Only keep candidates with a intersection/union score lower than a threshold.')
    parser.add_argument('--output-one', action='store_true', default=False, help='Randomly choosing one candidate per reference.')
    parser.add_argument('--json-input', action='store_true', default=False, help='Whether the input is JSON.')
    args = parser.parse_args()
    
    HIT_data = []
    result = []
    score = []

    ref_sents = []
    with open(args.ref_path, 'r', encoding='UTF-8') as f:
        for line in f:
            ref_sents.append(line.strip())

    with open(args.decoded_path, 'r', encoding='UTF-8') as f:
        counter = 0
        for line in f:
            if counter % system_num == 0:
                result.append([])
            if not args.json_input:
                ParaBank_line = line.strip('\n').split('\t')
                if ParaBank_line[1] != '':
                    #ParaBank_line[1] = detokenizer(ParaBank_line[1].split(' '))
                    #ParaBank_line[1] = fixTokenization(ParaBank_line[1])
                    if ParaBank_line[1] not in [entry[1] for entry in result[-1]]:
                        result[-1].append(ParaBank_line)
            else:
                ParaBank_json = json.loads(line.strip())
                pdb.set_trace()
            counter += 1
    print(len(result), len(ref_sents))
    assert len(result) == len(ref_sents)
    for i in range(len(ref_sents)):
        filtered = [x[1] for x in sorted([entry for entry in result[i] if calcIntersectionUnion(entry[1], ref_sents[i]) < args.diversity], key=lambda x:float(x[0]))]
        if len(filtered) == 0:
            filtered = [x[1] for x in sorted([entry for entry in result[i]], key=lambda x:float(x[0]))]
        if args.output_one:
            HIT_data.append([fixTokenization(detokenizer(filtered[0].split()))])
        else:
            HIT_data.append(filtered)
        #HIT_data.append([sorted([entry[1] for entry in result[i]], \
        #                key=lambda x: sentence_bleu([x.split()], ref_sents[i].split(), smoothing_function=smoother) \
        #                / brevity_penalty(len(ref_sents[i].split()), len(x.split())))[1]])
        #HIT_data.append([sorted([entry[1] for entry in result[i]], key=lambda x: calcIntersectionUnion(x, ref_sents[i]))[0]])
        #print(sentence_bleu([HIT_data[-1][0].split()], ref_sents[i].split(), smoothing_function=smoother))
        #print(calcIntersectionUnion(HIT_data[-1][0], ref_sents[i]))


    # write to output
    if args.output == "STDOUT":
        for row in HIT_data:
            print('\t'.join(row))
    else:
        with open(args.output, 'w', encoding='UTF-8') as f:
            wr = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
            for row in HIT_data:
                wr.writerow(row)

