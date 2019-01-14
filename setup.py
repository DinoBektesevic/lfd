from setuptools import setup

setup(
   name='lfd',
   version='1.0',
   description='Linear Feature Detector for Astronomical images',
   author='Dino Bektesevic',
    author_email='ljetibo@gmail.com',
   packages=['lfd'],  #same as name
   install_requires=[
       'numpy',
       'matplotlib',
       'scipy',
       'scikit-learn',
       'SQLAlchemy',
       'astropy',
       'fitsio',
       'opencv-python',
       'Pillow',
   ],
)
