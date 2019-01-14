Linear Feature Detector (LFD) library is a collection of packages that enable
user to detect and analyze linear features on astronomical images. The code was
designed to be run interactively, or at scale on a cluster and specifically
targets SDSS survey data and meteor trails therein.

LFD is a more complete version of LFDS that contains all of the never-published
features of LFDS. Except for the linear feature detection code in the detecttrails
module, most of the LFDS code was recoded from scratch and made compatible with
Python 3 and OpenCv 3.0. You can find the old LFDS code  here_.

.. _here: https://github.com/DinoBektesevic/LFDA

# Installation

Use the requirements.txt to create a new environment into which you can

.. code-block:: bash

   git clone https://github.com/DinoBektesevic/lfd.git

Import lfd and be on your merry way. 

Requirements
------------

Major requirements are as follows

* Python 3+
* OpenCV 3+
* NumPy 1.11+
* SciPy 0.19+
* Fitsio 0.9.7+
* SQLAlchemy 1.2.11+
* parts of Erin Sheldon's esutil_ and sdsspy_ utilities are bundled with the
  provided code. Some of the code might have been altered

.. _esutil: https://github.com/esheldon/sdsspy/
.. _sdsspy: https://github.com/esheldon/esutil

Running the code
----------------

Read the docs!

By default lfd is setup to work with SDSS files and directory structure. This
can be altered significantly, although complete departure from SDSS file and
directory structures are not supported out of the box.

Although slightly out of data much of the processing steps are still adequatly
described in::

  Bektesevic & Vinkovic, 2017, MNRAS, 1612.04748, Linear Feature Detection Algorithm for Astronomical Surveys - I. Algorithm description

To start processing use any of the following:

.. code-block:: python

     import lfd
     lfd.setup_detecttrails("~/boss")

     
     foo = lfd.detecttrails.DetectTrails(run=2888)
     foo = lfd.detecttrails.DetectTrails(run=2888, camcol=1)
     foo = lfd.detecttrails.DetectTrails(run=2888, camcol=1, filter='i')
     foo = lfd.detecttrails.DetectTrails(run=2888, camcol=1, filter='i', field=139)
     foo.process()


It is possible to change detection parameters of any step in the processing by

.. code-block:: python

     foo.params_dim
     foo.params_bright["debug"] = True
     foo.params_removestars["filter_caps"]["i"] = 20


Results are outputted to a file provided by the filepath `results`, by default
set to `results.txt`. Results file is a CSV file in which the detected
parameters. Results module provides functionality to parse these CSV files into
a database for which an SQLAlchemy ORM is provided.

.. code-block:: python

     lfd.results.connect2db("foo.db")
     lfd.results.from_file("results.txt")

     with results.session_scope() as s:
         s.query(Event).filter(Event.run=2888).all()

        fquery = query.filter(lfd.results.Frame.t.iso > '2009-09-27 10:06:10.430')
        f = fquery.all()
        lfd.results.deep_expunge_all(f, s)

LFD was designed to be able to handle processing large ammounts of data, in fact
it was used to process the entire SDSS database of images by using the Fermi
cluster at Astronomical Observatory Belgrade in Serbia. To make the creation of
scripts that ran LFD on the cluster easier createjobs module was written. By
default it is oriented towards running on that particular cluster, but it should
be easily adaptable to any Sun Grid cluster out there. 

.. code-block:: python

     jobs = cj.Jobs(500)
     jobs.create()
     There are no runs to create jobs from.
       Creating jobs for all runs in runlist.par file.
  
     Creating:
       765 jobs with 1 runs per job
       Queue:     standard
  	 Wallclock: 24:00:00
  	 Cputime:   48:00:00
  	 Ppn:       3
  	 Path:      /home/user/Desktop/.../jobs

which is of course very flexible

.. code-block:: python

   runs = [125, 99, 2888, 1447]
   cmd = """python3 -c "import detecttrails as dt;
            x = dt.DetectTrails($);
            x.params_bright['debug']=True;
            x.process()"""
   jobs = cj.Jobs(2, runs=runs, camcol=1, filter='i', command=cmd)
   jobs.create()

User will be notified about all important parameters that were set. LFD also
comes with Graphical User Interfaces through which users can create these jobs
via mouseclicks but also visually inspect their results by using the provided
specially designed image browser.

An analysis module is provided as well through which theoretical meteor profiles
can be generated as described in::

  Bektesevic & Vinkovic et. al. 2017 (arxiv: 1707.07223).

.. code-block:: python

     from lfd.analysis import profiles

     point = profiles.PointSource(100)
     seeing = profiles.GausKolmogorov(profiles.SDSSSEEING)
     defocus = profiles.FluxPerAngle(100, *profiles.SDSS)

     a = profiles.convolve(point, seeing, defocus)

     import matplotlib.pyplot as plt
     fig, ax = plt.subplots(1, 1)
     profiles.plot_profiles(ax, (point, seeing, defocus, a))
     plt.legend()
     plt.show()

All of this is, of course, just a quick overview of all functionalities. There
are many more details describing this and other useful utilities provided by LFD
availible in the documentation. 

# License

Copyright (C) 2018  Dino Bektesevic

This program is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this
program.  If not, see <http://www.gnu.org/licenses/>.


