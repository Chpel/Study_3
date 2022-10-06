#!/bin/bash
#SBATCH --job-name=Supmod_1
#SBATCH --output=Supmod_1_%a.txt
#SBATCH --time=01:00:00                  # Ограничение времени выполнения задачи (дни-часы:мин:сек)
module purge                             # Очистка переменных окружения

# Загрузка необходимых переменных окружения
module load gnu8 openmpi3

# Одновременный запуск задач
idx=$SLURM_ARRAY_TASK_ID
srun /home/iipchelintsev/Supmod/release1.out<input_data_$idx.txt

# done


# Ожидание завершения всех процессов
wait
