import numpy as np
cimport numpy as np

def quadratic_form(np.ndarray[double, ndim=2, mode='c'] A, np.ndarray[double, ndim=1, mode='c'] x):
    cdef int n = x.shape[0]
    cdef np.ndarray xTa = np.zeros(n, dtype=x.dtype)
    cdef double s = 0
    cdef double result = 0
    cdef int i
    cdef int j
    for i in range(n):
        s = 0
        for j in range(n):
            s += x[j] * A[j,i]
        xTa[i] = s
    for i in range(n):
        result += xTa[i] * x[i]
    return result