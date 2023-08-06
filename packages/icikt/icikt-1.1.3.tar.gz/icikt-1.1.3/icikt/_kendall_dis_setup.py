# Compile using:
# $ python3 _kendall_dis_setup.py build_ext --inplace

from setuptools import setup, Extension
import Cython.Build

setup(
          name = '_kendall_dis',
            ext_modules=[
                    Extension('_kendall_dis',
                                      sources=['_kendall_dis.pyx'],
                                                    language='c++')
                        ],
              cmdclass = {'build_ext': Cython.Build.build_ext}
              )
