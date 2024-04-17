from pcap_dataset import get_pcap_dataframe
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--ckpt", type=str, default="NousResearch/Llama-2-7b-chat-hf", help="Checkpoint path"
)
parser.add_argument(
    "--eval_dir", type=str, default="analysis/run", help="Path to save results"
)
args = parser.parse_args()

DATA_FILE = '/scratch/bae9wk/datasets/PCAP/CSV-01-12/01-12/test_set.csv'
CKPT = args.ckpt
EVAL_DIR = args.eval_dir

import os
os.environ['HF_HOME'] = '/scratch/bae9wk/datasets/.cache/'

for folder_name in [EVAL_DIR+'/Syn', EVAL_DIR+'/Benign']:
    if not os.path.exists(folder_name):
        os.makedirs(folder_name, exist_ok=True)

# Imports
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments, pipeline, logging
from peft import LoraConfig
from trl import SFTTrainer
import torch
import gc
from pcap_dataset import get_pcap_dataframe
from datasets import Dataset, load_dataset



compute_dtype = getattr(torch, "float16")
quant_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=compute_dtype, bnb_4bit_use_double_quant=False)

model = AutoModelForCausalLM.from_pretrained(CKPT, quantization_config=quant_config, device_map='auto')#{"": 0})
model.config.use_cache = False

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(CKPT, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

df = get_pcap_dataframe(DATA_FILE)
df = df.iloc[::-1] # Read from the back (unseen) examples

logging.set_verbosity(logging.CRITICAL)
end = '[/INST]'

with open(f"{EVAL_DIR}/info.txt", 'w') as f:
    f.write(f"""
            Evaluating {CKPT}
            Data file: {DATA_FILE}
            
            """)

for i in range(100):
    prompt = df.iloc[i]['text']
    label = 'Benign' if "benign" in prompt.lower() else 'Syn'

    prompt = prompt[: prompt.find(end)+len(end)]
    print(prompt)
    pipe = pipeline(task="text-generation", model=model, tokenizer=tokenizer, max_length=len(prompt)+200)
    result = pipe(prompt)

    with open(f"{EVAL_DIR}/{label}/{i}.txt", 'w') as f:
        f.write(result[0]['generated_text'])
        
    # f"<s>[INST] Who is Leonardo Da Vinci? [/INST]"