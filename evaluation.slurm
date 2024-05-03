#!/bin/bash -l

#SBATCH -A CollabRoboGroup
#SBATCH --array=500,2500,5000,7500,9750
#SBATCH -t 2:00:00
#SBATCH -p gpu
#SBATCH --gres=gpu:a100:1
#SBATCH -N 1
#SBATCH --cpus-per-task=30
#SBATCH --output=logs/eval-%A-%a.log
#SBATCH -J pcaplm
# 125 is max cpus per task
# #SBATCH --ntasks-per-node=1
# #SBATCH --begin=2023-10-29T3:00:00
# -C gpupod is included to only use A100s with 80 GB
# #SBATCH -C gpupod

module purge
module load anaconda
conda activate pcaplm
python evaluation.py --ckpt=results/run_update/checkpoint-${SLURM_ARRAY_TASK_ID} --eval_dir=analysis/checkpoint-${SLURM_ARRAY_TASK_ID}