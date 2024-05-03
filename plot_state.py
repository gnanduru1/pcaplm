import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import json

CKPT2 = 'results/run1/checkpoint-8000/trainer_state.json'
CKPT = 'results/run_update/checkpoint-10000/trainer_state.json'
name = 'final_plot'

data = []
with open(CKPT) as f:
    data = json.load(f)['log_history']
# Extract the data into separate lists
steps = [d["step"] for d in data]
grad_norms = [d["grad_norm"] for d in data]
learning_rates = [d["learning_rate"] for d in data]
losses = [d["loss"] for d in data]

with open(CKPT2) as f:
    data = json.load(f)['log_history']
# Extract the data into separate lists
steps2 = [d["step"] for d in data]
grad_norms2 = [d["grad_norm"] for d in data]
learning_rates2 = [d["learning_rate"] for d in data]
losses2 = [d["loss"] for d in data]

# Create the figure and subplots
# fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

## Gradient Norm Plot
figure(figsize=(10, 5), dpi=400)
s1, =plt.plot(steps, grad_norms)
s2, =plt.plot(steps2, grad_norms2)

plt.legend([s1,s2],["Final model", "Initial model"])

plt.xlabel("Step")
plt.ylabel("Gradient Norm")

# ## Loss Plot
# ax2.plot(steps, losses)
# ax2.set_title("Loss")
# ax2.set_xlabel("Step")
# ax2.set_ylabel("Loss")

# Adjust the spacing between subplots
#plt.subplots_adjust(hspace=0.5)

# Display the plot
plt.savefig(name+'_grad.png')
plt.savefig(name+'_grad.eps')

plt.clf()

s1, =plt.plot(steps, losses)
s2, =plt.plot(steps2, losses2)

plt.legend([s1,s2], ["Final model", "Initial model"])

plt.xlabel("Step")
plt.ylabel("Training Loss")

plt.savefig(name+'_loss.png')
plt.savefig(name+'_loss.eps')