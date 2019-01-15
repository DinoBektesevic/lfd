from setuptools import setup, find_packages

setup(
   name='lfd',
   version='1.0',
   description='Linear Feature Detector for Astronomical images',
   author='Dino Bektesevic',
   author_email='ljetibo@gmail.com',
   packages=find_packages(),  #same as name
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
