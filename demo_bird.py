from openai import OpenAI, BadRequestError
import traceback
import time
import argparse
import json
import os
import re
from tqdm import tqdm
from src import LookupAssistant, EvidenceAssistant, BirdToolBox, CoTF, NlqSplitAssistant

with open('./config/openai_api.json') as f:
    openai_cfg = json.load(f)
os.environ['OPENAI_API_KEY'] = openai_cfg['api_key']
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['ALL_PROXY'] = ''

from logging import getLogger, INFO
logger = getLogger(__name__)
logger.setLevel(INFO)
client = OpenAI()

def analyze_one_nlq(
        nlq:str,
        cotf: CoTF,
        db_tool_box:BirdToolBox,
        nlq_split_assistant:NlqSplitAssistant,
        lookup_assistant:LookupAssistant,
        evidence_assistant:EvidenceAssistant,
        pipeline:list = ['nlq_split', 'lookup', 'evidence'],
        max_round=5
    ):
    if 'nlq_split' in pipeline:
        # split the question
        nlq_split_assistant.clear_history_messages()
        nlq_split_assistant.init_conversation(nlq=nlq)
        nlq_split = nlq_split_assistant.respond()
        nlq_split = nlq_split['nlq_split']
        # clean the quotes
        whole_nlq_split = []
        while nlq != "":
            if len(nlq_split) == 0:
                whole_nlq_split.append(nlq)
                break
            phrase = nlq_split.pop(0)
            if phrase == nlq:
                whole_nlq_split.append(nlq)
                break
            split_list = nlq.split(phrase)
            if len(split_list) == 1:
                whole_nlq_split.append(nlq)
                break
            sentence, nlq = split_list
            sentence = sentence + phrase
            whole_nlq_split.append(sentence)
        whole_nlq_split = [phrase.replace('"', "'").replace('\n', " ").strip() for phrase in whole_nlq_split]
        logger.info(f"nlq: {nlq}")
        logger.info(f"nlq_split: {whole_nlq_split}")
    else:
        logger.info(f"nlq: {nlq}")
        logger.info("skip splitting the question.")
        nlq = nlq.replace('"', "'").replace('\n', "").strip()
        whole_nlq_split = [nlq]
    cotf.init_nlq_split(whole_nlq_split)

    # update the response format according to the split result
    json_schema = lookup_assistant.response_format['json_schema']
    json_schema['schema']['required'] = whole_nlq_split
    json_schema['schema']['properties'] = {phrase: {"$ref": "#/$defs/thought"} for phrase in whole_nlq_split}
    lookup_assistant.response_format['json_schema'] = json_schema
    lookup_assistant.update_assistant(response_format=lookup_assistant.response_format)

    # pipeline
    db_schema = db_tool_box.get_basic_info()

    if 'lookup' not in pipeline:
        raise ValueError("The pipeline must contain 'lookup'.")
    lookup_assistant.clear_history_messages()
    lookup_assistant.init_conversation(db_schema=db_schema)
    
    # analyze
    lookup_assistant.add_message(f"here is the user's question: {nlq}")
    for i in range(max_round):
        lookup_assis_resp = lookup_assistant.respond()
        cotf.record_thoughts(lookup_assis_resp, have_analysis=have_analysis)
        lookup_results_dict, continue_lookup = db_tool_box.execute_lookups(lookup_assis_resp, cotf.tool_chain)
        cotf.record_facts(lookup_results_dict, step=i)
        if not continue_lookup:
            break

        lookup_assistant.add_message(f"here is the lookup results: {json.dumps(lookup_results_dict)}")

    if 'evidence' in pipeline:
        # generate evidence
        evidence_assistant.clear_history_messages()
        evidence_assistant.init_conversation(question=nlq, cotf=json.dumps(cotf.cotf))
        evidence = evidence_assistant.respond()
        logger.info(f"evidence: {evidence}")
    else:
        logger.info("skip generating evidence.")
        evidence = None

    return evidence, cotf.cotf


def generate_all_evidence(TDataBaseToolBox, output_dir, args):
    nlq_split_assistant = NlqSplitAssistant(config_file=args.nlq_split_config_file, client=client, thread_mode=args.thread_mode)
    lookup_assistant = LookupAssistant(config_file=args.lookup_config_file, client=client, thread_mode=args.thread_mode)
    evidence_assistant = EvidenceAssistant(config_file=args.evidence_config_file, client=client, thread_mode=args.thread_mode)
    nlq_split_assistant.load_assistant()
    lookup_assistant.load_assistant()
    evidence_assistant.load_assistant()
    nlq_split_assistant.load_thread()
    lookup_assistant.load_thread()
    evidence_assistant.load_thread()

    results = []

    with open(args.input_file) as f:
        input_data = json.load(f)
    if args.mode == 'train':
        for i, item in enumerate(input_data):
            item['question_id'] = i

    # Continue from the break point if there are results.
    if os.path.exists(f'{output_dir}/DIVER_evidence_results.json'):
        with open(f'{output_dir}/DIVER_evidence_results.json') as f:
            results = json.load(f)
        input_data = [item for item in input_data if item['question_id'] > results[-1]['question_id']]
        logger.info(f'Continue from the break point. The last completed question id is {results[-1]["question_id"]}.')

    if args.skip_non_empty:
        input_data = [item for item in input_data if 'Evidence is empty because' in item['DIVER_evidence']]
        logger.info(f'Skip the non-empty evidence. The number of questions to analyze is {len(input_data)}.')


    if args.pipeline == ['evidence']:
        for item in tqdm(input_data):
            # generate evidence
            evidence_assistant.clear_history_messages()
            evidence_assistant.init_conversation(question=item['question'], cotf=json.dumps(item['DIVER_cotf']))
            evidence = evidence_assistant.respond()
            item['DIVER_evidence'] = evidence
            results.append(item)
            with open(f'{output_dir}/DIVER_evidence_results.json', 'w') as f:
                json.dump(results, f, indent=4)
        
        return results
            


    db_id = None
    for item in tqdm(input_data):
        if item['question_id'] < args.start_idx:
            continue

        if item['db_id'] != db_id:
            db_id = item['db_id']
            db_file = f'/{PATH_TO_DIVER_PROJECT}/DIVER/data/BIRD/{args.mode}/{args.mode}_databases/{db_id}/{db_id}.sqlite'
            db_tool_box = TDataBaseToolBox(db_file)
            
        nlq = item['question']
        num_retry = 0
        while num_retry < 3:
            num_retry += 1
            try:
                cotf = CoTF()
                evidence, cotf_dict = analyze_one_nlq(nlq, cotf, db_tool_box, nlq_split_assistant, lookup_assistant, evidence_assistant, args.pipeline)
            except BadRequestError as e:
                logger.error(f'Error in analyzing question {item["question_id"]}: {e}. Try to resolve:')
                match_res = re.match(r"Can't add messages to (.*) while a run (.*) is active.", e.body['message'])
                if match_res is not None:
                    logger.error("\tTry to resolve by creating new thread.")
                    wrong_thread_id = match_res.group(1)
                    for assistant in [nlq_split_assistant, lookup_assistant, evidence_assistant]:
                        if assistant.thread_id == wrong_thread_id:
                            assistant.refresh_thread()
                evidence = f"Evidence is empty because error in analyzing the question: {e}"
                cotf_dict = cotf.cotf
            except Exception as e:
                logger.error(f'Error in analyzing question {item["question_id"]}: {e}. Retry {num_retry}.')
                evidence = f"Evidence is empty because error in analyzing the question: {e}" + traceback.format_exc()
                cotf_dict = cotf.cotf
                traceback.print_exc()
            else:
                break

        item['DIVER_evidence'] = evidence
        item['DIVER_cotf'] = cotf_dict
        results.append(item)

        if num_retry == 3:
            logger.error(f'Retried 3 times. Failed to analyze question {item["question_id"]}.')
            logger.info("Save temp file and continue.")
            
        with open(f'{output_dir}/DIVER_evidence_results.json', 'w') as f:
            json.dump(results, f, indent=4)

    return results


if __name__ == '__main__':
    # parse the arguments
    parser = argparse.ArgumentParser(description='Generate evidence for BIRD dataset.')
    parser.add_argument('--input_file', type=str, required=True, help='The input file path.')
    parser.add_argument('--mode', type=str, required=True, help='The mode of the dataset.')
    parser.add_argument('--pipeline', nargs='+', help='The pipeline to use.')
    parser.add_argument('--start_idx', type=int, default=0, help='The start index of the dataset.')
    parser.add_argument('--nlq_split_config_file', type=str, default='./config/split_nlq_assistant.json', help='The config file for the NlqSplitAssistant.')
    parser.add_argument('--lookup_config_file', type=str, default='./config/lookup_assistant.json', help='The config file for the LookupAssistant.')
    parser.add_argument('--evidence_config_file', type=str, default='./config/evidence_assistant/default.json', help='The config file for the EvidenceAssistant.')
    parser.add_argument('--thread_mode', type=str, default='holding', help='The thread mode for the assistants.')
    parser.add_argument('--skip_non_empty', type=bool, default=False, help='Whether to skip the non-empty evidence.')
    args = parser.parse_args()

    # for w/o cot ablation
    global have_analysis
    have_analysis = True
    if "w.o cot" in args.lookup_config_file:
        have_analysis = False

    # set the output directory
    data_dir = args.input_file[:args.input_file.rfind('/')]
    time_str = time.strftime("%Y%m%d-%H:%M:%S", time.localtime())
    output_dir = f'{data_dir}/{time_str}'
    os.makedirs(output_dir)

    # save the config
    with open(f'{output_dir}/-args.json', 'w') as f:
        json.dump(vars(args), f, indent=4)

    ### test
    results = generate_all_evidence(BirdToolBox, output_dir, args)