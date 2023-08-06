from setuptools import setup, find_packages

version = "1.5.7"
description = "This module returns the equation of the linear fitted curve!"
with open("README.md", 'r', encoding = 'utf-8') as fh:
    lond_description = fh.read()

setup(name = "lineq",
      version = version,
      author = "Amirreza Soltani",
      author_email = "charleswestmorelandPB1@gmail.com",
      description = description,
      long_description = lond_description,
      long_description_content_type="text/markdown",
      packages = find_packages(where = "src"),
      install_requires = ['numpy'],
      keywords = ['python', 'curve fitting', 'equation'],
      classifiers = ['Programming Language :: Python :: 3',
                    'License :: OSI Approved :: MIT License',
                    'Operating System :: Unix',
                    'Operating System :: MacOS :: MacOS X',
                    'Operating System :: Microsoft :: Windows'],
      package_dir={"": "src"},  
      python_requires = '>=3.6'
 )