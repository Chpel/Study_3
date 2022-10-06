from time import time
import quad_form


def benchmark(nrepeat, A, b):
	start = time()
	for i in range(nrepeat):
		res = quad_form.quadratic_form(A, b)
	end = time()
	ms_per_run = (end - start) * 1000 / nrepeat
	return res, ms_per_run
	
    
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
res, time = benchmark(1000, a, b)
print(f'timing: {time}')
print(f'result: {res}')
