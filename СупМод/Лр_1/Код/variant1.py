import numpy as np
from datetime import datetime
from time import time

def benchmark(fn, nrepeat, *args):
	start = time()
	for i in range(nrepeat):
		res = fn(*args)
	end = time()
	ms_per_run = (end - start) * 1000 / nrepeat
	return res, ms_per_run

def quadratic_form(A,x):
	n = x.shape[0]
	xTa = np.zeros(n)
	for i in range(n):
		sum = 0
		for j in range(n):
			sum += x[j] * A[j][i]
		xTa[i] = sum
	result = 0
	for i in range(n):
		result += xTa[i] * x[i]
	return result

	

n = int(input())
a = []
for i in range(n):
	a_i = list(map(float, input().split(' ')))
	if len(a_i) == n:
		a.append(a_i)
	else:
		print('Значения матрицы заполнены неверно!')
		exit()
x = list(map(float, input().split(' ')))
if len(x) != n:
	print('Значения вектора заполнены неверно!')
	exit()


np_A = np.array(a)
np_x = np.array(x)
res, time = benchmark(quadratic_form, 1000, np_A, np_x)
print(f'timing: {time}')
print(f'result: {res}')
