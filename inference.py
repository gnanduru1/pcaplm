from pcap_dataset import get_pcap_dataframe
DATA_FILE = '/scratch/bae9wk/datasets/PCAP/CSV-01-12/01-12/small_syn.csv'
CKPT = '/scratch/bae9wk/PCAPLM/results/checkpoint-44725'
import os
os.environ['HF_HOME'] = '/scratch/bae9wk/datasets/.cache/'

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

logging.set_verbosity(logging.CRITICAL)
delim = '[/INST]'
prompt = df.iloc[0]['text']
prompt = prompt[: prompt.find(delim)+len(delim)]

print(prompt)
pipe = pipeline(task="text-generation", model=model, tokenizer=tokenizer, max_length=200)
result = pipe(prompt)
print(result[0]['generated_text'])