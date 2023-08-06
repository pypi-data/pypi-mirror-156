#!/usr/bin/env python3

from setuptools import setup, Extension
long_description = open("README.rst").read()

setup(name="Chips-python",
      version="2.2.3",
      description="Design hardware with Python",
      long_description=long_description,

      author="Jon Dawson",
      author_email="chips@jondawson.org.uk",
      url="http://benfre.github.io/Chips/",
      download_url="http://github.com/benfre/Chips",
      keywords=["Verilog", "FPGA", "C", "HDL", "Synthesis", "VHDL"],
      install_requires=["numpy"],
      ext_modules = [
            Extension("_chips_c", ["chips_c/chips_c.c", "chips_c/chips_c_wrap.c"])
      ],
      py_modules = [
          "chips_c"
      ],
      classifiers = [
          "Programming Language :: Python",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Intended Audience :: Science/Research",
          "Intended Audience :: Developers",
          "Development Status :: 3 - Alpha",
          "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
          "Topic :: Software Development :: Embedded Systems",
          "Topic :: Software Development :: Code Generators",
      ],
      packages=[
          "chips",
          "chips.chipsweb",
          "chips.compiler",
          "chips.api",
          "chips.components",
          "chips.utils"
      ],
      package_data = {
          "chips.compiler":[
              "builtins.h",
              "include/*.h",
          ],
          "chips.utils":[
              "icons/*.png",
          ],
          "chips.chipsweb":[
              "templates/*.html",
              "static/*",
          ],
          "chips.components":[
              "verilog/*.v",
          ]
      },
      scripts=[
          "c2verilog",
          "csim"
      ]
)
