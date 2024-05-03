from pcap_dataset import get_pcap_dataframe
DATA_FILE = '/scratch/bae9wk/datasets/syn-no-syn.csv'
#CKPT = '/scratch/bae9wk/PCAPLM/results/checkpoint-44725'

#CKPT = 'results/checkpoint-136750'
#CKPT = "NousResearch/Llama-2-7b-chat-hf"
CKPT = 'results/run_update/checkpoint-9750'
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

dataset = load_dataset("csv", data_files=DATA_FILE, split='train')
print(len(dataset))
1/0


compute_dtype = getattr(torch, "float16")
quant_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=compute_dtype, bnb_4bit_use_double_quant=False)

model = AutoModelForCausalLM.from_pretrained(CKPT, quantization_config=quant_config, device_map='auto')#{"": 0})
model.config.use_cache = False

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(CKPT, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

logging.set_verbosity(logging.CRITICAL)
end = '[/INST]'
prompt = df.iloc[0]['text']
prompt = prompt[: prompt.find(end)+len(end)]

print(prompt)
pipe = pipeline(task="text-generation", model=model, tokenizer=tokenizer, max_length=len(prompt)+200)
result = pipe(prompt)

print(result[0]['generated_text'])
    
   # f"<s>[INST] Who is Leonardo Da Vinci? [/INST]"