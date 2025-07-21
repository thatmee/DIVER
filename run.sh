# -----------------
#    input file
# -----------------

input_file="PATH_TO_DEV.JSON"
mode="dev"


pipeline="nlq_split lookup evidence"  # [nlq_split, lookup, evidence]

nlq_split_config_file="./config/split_nlq_assistant.json"
lookup_config_file="./config/lookup_assistant.json"

# --------------------
#   evidence configs
# --------------------
# evidence_config_file="./config/evidence_assistant/default.json"
evidence_config_file="./config/evidence_assistant/few_shots_nlq_split.json"

### other configs
thread_mode="holding"  # [holding, sep_conv]
start_idx=0


CUDA_VISIBLE_DEVICES=1 python demo_bird.py \
    --input_file $input_file \
    --mode $mode \
    --pipeline $pipeline \
    --start_idx $start_idx \
    --nlq_split_config_file $nlq_split_config_file \
    --lookup_config_file $lookup_config_file \
    --evidence_config_file $evidence_config_file \
    --thread_mode $thread_mode