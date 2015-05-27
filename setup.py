from distutils.core import setup
from Cython.Build import cythonize

setup(
  name = 'MClone',
  ext_modules = cythonize("noise.pyx"),
)
