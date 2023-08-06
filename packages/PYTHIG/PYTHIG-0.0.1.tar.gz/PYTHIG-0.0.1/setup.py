from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Python made easy!'
LONG_DESCRIPTION = 'Pythig makes python coding easier! Installs a range of packages for you, and does AI changes!'

# Setting Up
setup(name="PYTHIG", version=VERSION, author="undefined", author_email="<ericmuzyk@icloud.com>", description=DESCRIPTION
      , long_description=LONG_DESCRIPTION, packages=find_packages(), install_requires=[], keywords=['python',
                                                                                                    'made_easy',
                                                                                                    'pythig'],
      classifiers=["Development Status :: 3 - Alpha",
                   "Intended Audience :: Education",
                   "Programming Language :: Python :: 2",
                   "Programming Language :: Python :: 3",
                   "Operating System :: MacOS :: MacOS X",
                   "Operating System :: Microsoft :: Windows"
                   ]
      )
