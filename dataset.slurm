#!/bin/bash -l

#SBATCH -A CollabRoboGroup
#SBATCH --array=0
#SBATCH -t 72:00:00
#SBATCH -p standard
#SBATCH -N 1
#SBATCH --cpus-per-task=30
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
python pcap_dataset.py --save_to=/scratch/bae9wk/datasets/PCAP/CSV-01-12/01-12/augment.csv --read_from=/scratch/bae9wk/datasets/PCAP/CSV-01-12/01-12/Syn.csv