from codecs import open
from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='serpy',
    version='0.3.0',
    description='ridiculously fast object serialization',
    long_description=long_description,
    url='https://github.com/clarkduvall/serpy',
    author='Clark DuVall',
    author_email='clark.duvall@gmail.com',
    license='MIT',
    install_requires=['six'],
    test_suite='tests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    keywords=('serialization', 'rest', 'json', 'api', 'marshal',
              'marshalling', 'validation', 'schema', 'fast'),
    packages=find_packages(exclude=[
        'contrib',
        'docs',
        'tests*',
        'benchmarks'
    ]),
)
