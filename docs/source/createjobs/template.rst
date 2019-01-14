Templates
---------

By default the opened template is called "generic" and can be found in the same
folder this module resides in. Since it's neccesary to change a lot of
parameters, especially paths, template can be edited, or a new one can be
provided in its place.

Specifying `template_path` at Job class instantiation time will instruct the
writer to substitute the template used.

When writing your own template, to avoid error reports, you have to specify all
parameters in the new template that this class can change. Parameters are
uppercase single words, i.e: JOBNAME, QUEUE, NODEFLAG

.. code-block:: bash

    #!/usr/bin/ksh
    #PBS -N JOBNAME
    #PBS -S /usr/bin/ksh
    #PBS -q QUEUE
    #PBS -l nodes=NODEFLAG:ppn=PPN
    #PBS -l walltime=WALLCLOCK,cput=CPUTIME

Not all enviroment paths in the template are changable throught this class. This
was done to avoid confusion and additional complexity of how working paths are
handles, since on a cluster greater flexibility is provided by the filesystem,
that is usually tricky to nicely wrap in Python. Additionally, most of the
used directories will often share the same top directory path, while individual
jobs will only differ at the level of particular target subdirectory inside the
targeted top directory. Such paths can be edited in place in the template, for
example::

    cp *.txt /home/fermi/$user/run_results/$JOB_ID/

Bellow is the full content of the generic template provided with the module:

.. include:: generic.txt
   :literal:
