from distutils.core import setup
from distutils.extension import Extension

import numpy
from Cython.Distutils import build_ext

setup(
    name="quadratic_form",
    cmdclass={"build_ext": build_ext},
    ext_modules=[Extension(
        "quadratic_form",
        ["quadratic_form.pyx"],
        libraries=["m"],
        extra_compile_args=["-ffast-math"],
        include_dirs=[numpy.get_include()]
    )]
)