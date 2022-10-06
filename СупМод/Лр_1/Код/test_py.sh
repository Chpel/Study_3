#!/bin/bash
#SBATCH --job-name=Supmod_1py
#SBATCH --output=Supmod_1py_%a.txt
#SBATCH --time=01:00:00                 # Ограничение времени выполнения задачи (дни-часы:мин:сек)
module purge                             # Очистка переменных окружения

# Загрузка необходимых переменных окружения
module load Python/Google_Colab

# Одновременный запуск задач
idx=$SLURM_ARRAY_TASK_ID
python /home/iipchelintsev/Supmod/variant1.py<input_data_$idx.txt

# done


# Ожидание завершения всех процессов
wait
