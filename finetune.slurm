#!/bin/bash -l

#SBATCH -A CollabRoboGroup
#SBATCH --array=0
#SBATCH -t 72:00:00
#SBATCH -p gpu
#SBATCH --gres=gpu:a100:8
#SBATCH --constraint=a100_80gb
#SBATCH -N 1
#SBATCH --cpus-per-task=120
#SBATCH --output=logs/log-%A-%a.log
#SBATCH -J pcaplm
# 125 is max cpus per task
# #SBATCH --ntasks-per-node=1
# #SBATCH --begin=2023-10-29T3:00:00
# -C gpupod is included to only use A100s with 80 GB
# #SBATCH -C gpupod

module purge
module load anaconda
conda activate pcaplm
python finetune.py