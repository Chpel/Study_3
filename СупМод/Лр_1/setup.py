from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("quad_form.pyx"),
)