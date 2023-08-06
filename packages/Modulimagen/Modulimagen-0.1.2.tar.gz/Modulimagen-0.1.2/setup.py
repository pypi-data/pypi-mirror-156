from setuptools import setup

setup(
    name='Modulimagen',
    url='https://github.com/RubenSab/Modulimagen',
    readme='README.md',
    author='Ruben Sabatini',
    author_email='rubensabatini2005@gmail.com',
    py_modules=['Modulimagen'],
    install_requires=['numpy', 'noise'],
    version='0.1.2',
    license='LGPL-2.1',
    description='A python module that contains functions which can be mixed and applied in sequence for generating matrices (which can be converted into images) in a modular way.',
    long_description='more info at https://github.com/RubenSab/Modulimagen')
