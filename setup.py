from setuptools import setup, find_packages

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='lfd',
    version='1.0.2',
    description='Linear Feature Detector for Astronomical images',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Dino Bektesevic',
    author_email='ljetibo@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'numpy',
        'matplotlib',
        'scipy',
        'scikit-learn',
        'SQLAlchemy',
        'astropy',
        'fitsio',
        'Pillow',
        'opencv-python',
    ],
)
