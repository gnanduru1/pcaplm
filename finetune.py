# Configure locations of huggingface cache and dataset
DATA_FILE = '/scratch/bae9wk/datasets/syn-no-syn.csv'
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

#Force garbage collection
gc.collect()

def display_cuda_memory():
    print("\n--------------------------------------------------\n")
    print("torch.cuda.memory_allocated: %fGB"%(torch.cuda.memory_allocated(0)/1024/1024/1024))
    print("torch.cuda.memory_reserved: %fGB"%(torch.cuda.memory_reserved(0)/1024/1024/1024))
    print("torch.cuda.max_memory_reserved: %fGB"%(torch.cuda.max_memory_reserved(0)/1024/1024/1024))
    print("\n--------------------------------------------------\n")

# Install required libraries (uncomment the following line when running in a notebook environment)

#For PyTorch memory management add the following code

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:1024" #1024
os.environ["NCCL_DEBUG"] ="INFO"
print("Imported libraries")


# Define model, dataset, and new model name
base_model = "NousResearch/Llama-2-7b-chat-hf"
new_model = "llama-2-7b-chat-pcap"

# Load dataset
dataset = load_dataset("csv", data_files=DATA_FILE, split='train')
#dataset = Dataset.from_pandas(get_pcap_dataframe(DATA_DIR))
print("Loaded dataset")

# 4-bit Quantization Configuration
compute_dtype = getattr(torch, "float16")
quant_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=compute_dtype, bnb_4bit_use_double_quant=False)

# Load model with 4-bit precision
model = AutoModelForCausalLM.from_pretrained(base_model, quantization_config=quant_config, device_map='auto')#{"": 0})
model.config.use_cache = False
model.config.pretraining_tp = 1
print("Setup model")

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

# Set PEFT Parameters
peft_params = LoraConfig(lora_alpha=16, lora_dropout=0.1, r=64, bias="none", task_type="CAUSAL_LM")

# Define training parameters
pd = 4
training_params = TrainingArguments(output_dir="./results/run_update2", num_train_epochs=1, per_device_train_batch_size=pd, gradient_accumulation_steps=1, optim="paged_adamw_32bit", save_steps=250, logging_steps=5, learning_rate=2e-5, weight_decay=0.001, fp16=False, bf16=False, max_grad_norm=0.3, max_steps=-1, warmup_ratio=0.03, group_by_length=True, lr_scheduler_type="polynomial", report_to="tensorboard")

# Initialize the trainer
trainer = SFTTrainer(model=model, train_dataset=dataset, peft_config=peft_params, dataset_text_field="text", max_seq_length=None, tokenizer=tokenizer, args=training_params, packing=False)
print("Initialized trainer")

#Force clean the pytorch cache
gc.collect()

torch.cuda.empty_cache()

# Train the model
print("Training model")
trainer.train()

# Save the model and tokenizer
trainer.model.save_pretrained(new_model)
trainer.tokenizer.save_pretrained(new_model)

# Evaluate the model (optional, requires Tensorboard installation)
# from tensorboard import notebook
# log_dir = "results/runs"
# notebook.start("--logdir {} --port 4000".format(log_dir))

# Test the model
logging.set_verbosity(logging.CRITICAL)
prompt = "Who is Leonardo Da Vinci?"
pipe = pipeline(task="text-generation", model=model, tokenizer=tokenizer, max_length=200)
result = pipe(f"<s>[INST] {prompt} [/INST]")
print(result[0]['generated_text'])