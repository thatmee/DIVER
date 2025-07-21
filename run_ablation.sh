# -----------------
#  general config
# -----------------
input_file="/{PATH_TO_DIVER_PROJECT}/DIVER/data/BIRD-small-dev_10%/dev.json"
mode="dev"
pipeline="nlq_split lookup evidence"  # [nlq_split, lookup, evidence]
nlq_split_config_file="./config/split_nlq_assistant.json"
evidence_config_file="./config/evidence_assistant/few_shots_nlq_split.json"
thread_mode="holding"  # [holding, sep_conv]
start_idx=0

device=0


# -------------------
#  ablation of tools
# -------------------


# w/o value_in
lookup_config_file="./config/ablation_of_tools_config/w.o value_in/lookup_assistant.json"

CUDA_VISIBLE_DEVICES=$device python demo_bird.py --input_file $input_file --mode $mode --pipeline $pipeline --start_idx $start_idx --nlq_split_config_file $nlq_split_config_file --lookup_config_file "$lookup_config_file" --evidence_config_file $evidence_config_file --thread_mode $thread_mode


# w/o sim_value_in
lookup_config_file="./config/ablation_of_tools_config/w.o sim_value_in/lookup_assistant.json"

CUDA_VISIBLE_DEVICES=$device python demo_bird.py --input_file $input_file --mode $mode --pipeline $pipeline --start_idx $start_idx --nlq_split_config_file $nlq_split_config_file --lookup_config_file "$lookup_config_file" --evidence_config_file $evidence_config_file --thread_mode $thread_mode


# w/o uniq_value
lookup_config_file="./config/ablation_of_tools_config/w.o uniq_value/lookup_assistant.json"

CUDA_VISIBLE_DEVICES=$device python demo_bird.py --input_file $input_file --mode $mode --pipeline $pipeline --start_idx $start_idx --nlq_split_config_file $nlq_split_config_file --lookup_config_file "$lookup_config_file" --evidence_config_file $evidence_config_file --thread_mode $thread_mode


# w/o head
lookup_config_file="./config/ablation_of_tools_config/w.o head/lookup_assistant.json"

CUDA_VISIBLE_DEVICES=$device python demo_bird.py --input_file $input_file --mode $mode --pipeline $pipeline --start_idx $start_idx --nlq_split_config_file $nlq_split_config_file --lookup_config_file "$lookup_config_file" --evidence_config_file $evidence_config_file --thread_mode $thread_mode


# w/o random
lookup_config_file="./config/ablation_of_tools_config/w.o random/lookup_assistant.json"

CUDA_VISIBLE_DEVICES=$device python demo_bird.py --input_file $input_file --mode $mode --pipeline $pipeline --start_idx $start_idx --nlq_split_config_file $nlq_split_config_file --lookup_config_file "$lookup_config_file" --evidence_config_file $evidence_config_file --thread_mode $thread_mode


# w/o if_null
lookup_config_file="./config/ablation_of_tools_config/w.o if_null/lookup_assistant.json"

CUDA_VISIBLE_DEVICES=$device python demo_bird.py --input_file $input_file --mode $mode --pipeline $pipeline --start_idx $start_idx --nlq_split_config_file $nlq_split_config_file --lookup_config_file "$lookup_config_file" --evidence_config_file $evidence_config_file --thread_mode $thread_mode


# w/o info
lookup_config_file="./config/ablation_of_tools_config/w.o info/lookup_assistant.json"

CUDA_VISIBLE_DEVICES=$device python demo_bird.py --input_file $input_file --mode $mode --pipeline $pipeline --start_idx $start_idx --nlq_split_config_file $nlq_split_config_file --lookup_config_file "$lookup_config_file" --evidence_config_file $evidence_config_file --thread_mode $thread_mode


# w/o sim_columns
lookup_config_file="./config/ablation_of_tools_config/w.o sim_columns/lookup_assistant.json"

CUDA_VISIBLE_DEVICES=$device python demo_bird.py --input_file $input_file --mode $mode --pipeline $pipeline --start_idx $start_idx --nlq_split_config_file $nlq_split_config_file --lookup_config_file "$lookup_config_file" --evidence_config_file $evidence_config_file --thread_mode $thread_mode


# -------------------
#  ablation of cotf
# -------------------


# w/o cot

lookup_config_file="./config/ablation_of_cotf_config/w.o cot/lookup_assistant.json"

CUDA_VISIBLE_DEVICES=$device python demo_bird.py --input_file "$input_file" --mode $mode --pipeline $pipeline --start_idx $start_idx --nlq_split_config_file $nlq_split_config_file --lookup_config_file "$lookup_config_file" --evidence_config_file $evidence_config_file --thread_mode $thread_mode



# ------------------------
#  ablation of tool desc
# ------------------------

# w/o tool desc
lookup_config_file="./config/ablation_of_tool_prompt/w.o tool_desc/lookup_assistant.json"

CUDA_VISIBLE_DEVICES=$device python demo_bird.py --input_file $input_file --mode $mode --pipeline $pipeline --start_idx $start_idx --nlq_split_config_file $nlq_split_config_file --lookup_config_file "$lookup_config_file" --evidence_config_file $evidence_config_file --thread_mode $thread_mode


# w/o param
lookup_config_file="./config/ablation_of_tool_prompt/w.o param/lookup_assistant.json"

CUDA_VISIBLE_DEVICES=$device python demo_bird.py --input_file $input_file --mode $mode --pipeline $pipeline --start_idx $start_idx --nlq_split_config_file $nlq_split_config_file --lookup_config_file "$lookup_config_file" --evidence_config_file $evidence_config_file --thread_mode $thread_mode


# w/o scenario
lookup_config_file="./config/ablation_of_tool_prompt/w.o scenario/lookup_assistant.json"

CUDA_VISIBLE_DEVICES=$device python demo_bird.py --input_file $input_file --mode $mode --pipeline $pipeline --start_idx $start_idx --nlq_split_config_file $nlq_split_config_file --lookup_config_file "$lookup_config_file" --evidence_config_file $evidence_config_file --thread_mode $thread_mode