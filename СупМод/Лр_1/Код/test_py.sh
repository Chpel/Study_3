#!/bin/bash
#SBATCH --job-name=Supmod_1py
#SBATCH --output=Supmod_1py_%a.txt
#SBATCH --time=01:00:00                 # ����������� ������� ���������� ������ (���-����:���:���)
module purge                             # ������� ���������� ���������

# �������� ����������� ���������� ���������
module load Python/Google_Colab

# ������������� ������ �����
idx=$SLURM_ARRAY_TASK_ID
python /home/iipchelintsev/Supmod/variant1.py<input_data_$idx.txt

# done


# �������� ���������� ���� ���������
wait
